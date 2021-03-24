#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
A script which prepares, executes and controls maintenance tasks on systems
managed with Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import, print_function

import argparse
import logging
import json
import time
import os
import getpass
import datetime
import yaml
from . import __version__, get_credentials
from .exceptions import (EmptySetException,
InvalidCredentialsException, SessionException, SnapshotExistsException,
UnsupportedRequestException)
from .management import get_virtualization_client
from .management.foreman import ForemanAPIClient
from .monitoring import get_monitoring_client
from .network import validate_hostname
from .reports import is_valid_report, load_report, write_report

"""
ForemanAPIClient: Foreman API client handle
"""
LOGGER = logging.getLogger('katprep_maintenance')
"""
logging: Logger instance
"""
LOG_LEVEL = None
"""
logging: Logger level
"""
SAT_CLIENT = None
"""
ForemanAPIClient: Foreman API client handle
"""
VIRT_CLIENTS = {}
"""
dict: libvirt API client handles
"""
MON_CLIENTS = {}
"""
dict: Nagios CGI client handles
"""
REPORT = None
"""
dict: Snapshot report
"""
REPORT_PREFIX = ""
"""
str: Date prefix for snapshots and downtimes
"""



def is_blacklisted(host, blacklist):
    """
    This function checks whether a host is matched by an exclude pattern
    """
    for entry in blacklist:
        if entry.replace("*", "").replace("%", "") in host:
            return True
    return False


def manage_host_preparation(options, host, cleanup=False):
    """
    This function prepares or cleans up maintenance tasks for a particular
    host. This includes creating/removing snapshots and scheduled downtimes.

    :param host: hostname
    :type host: str
    :param cleanup: Flag whether preparations should be undone (default: no)
    :type cleanup: bool
    """
    snapshots_to_skip = [None, "", "fixmepls"]
    snapshot = host.get_param("katprep_virt_snapshot")

    #create snapshot if applicable
    if not options.virt_skip_snapshot and snapshot not in snapshots_to_skip:
        LOGGER.debug(
            "Host '%s' needs to be protected by a snapshot", host
        )

        vm_name = host.virtualisation_id
        snapshot_name = "katprep_{}".format(REPORT_PREFIX)

        if options.generic_dry_run:
            if cleanup:
                LOGGER.info(
                    "Host '%s' --> remove snapshot (%s@%s)",
                        host, snapshot_name, vm_name
                )
            else:
                LOGGER.info(
                    "Host '%s' --> create snapshot (%s@%s)",
                    host, snapshot_name, vm_name
                )
        else:
            virt_address = host.get_param("katprep_virt")
            virt_client = VIRT_CLIENTS[virt_address]

            try:
                if cleanup:
                    # remove snapshot
                    virt_client.remove_snapshot(vm_name, snapshot_name)
                else:
                    # create snapshot
                    virt_client.create_snapshot(
                        vm_name, snapshot_name,
                        "Snapshot created automatically by katprep"
                    )
            except InvalidCredentialsException as err:
                LOGGER.error("Invalid crendentials supplied")
            except SnapshotExistsException as err:
                LOGGER.info("Snapshot for host '%s' already exists: %s", host, err)
            except EmptySetException as err:
                LOGGER.info("Snapshot for host '%s' already removed: %s", host, err)
            except SessionException as err:
                LOGGER.error("Unable to manage snapshot for host '%s': %s", host, err)

    #get errata reboot flags
    try:
        errata_reboot = [x["reboot_suggested"] for x in REPORT[host]["errata"]]
    except KeyError:
        #no reboot suggested
        errata_reboot = []

    #schedule downtime if applicable
    #TODO: only schedule downtime if a patch suggests it?
    if options.mon_skip_downtime:
        return

    monitoring_address = host.get_param("katprep_mon")
    unwanted_monitoring_addresss = [None, "", "fixmepls"]

    if monitoring_address not in unwanted_monitoring_addresss or \
        (options.mon_suggested and True in errata_reboot):

        LOGGER.debug(
            "Downtime needs to be scheduled for host '%s'", host
        )

        if options.generic_dry_run:
            if cleanup:
                LOGGER.info("Host '%s' --> remove downtime", host)
            else:
                LOGGER.info("Host '%s' --> schedule downtime", host)
        else:
            monitoring_client = MON_CLIENTS[monitoring_address]
            try:
                if cleanup:
                    monitoring_client.remove_downtime(host)
                else:
                    monitoring_client.schedule_downtime(host,
                                                        hours=options.mon_downtime)
            except InvalidCredentialsException as err:
                LOGGER.error("Unable to maintain downtime: '%s'", err)
            except UnsupportedRequestException as err:
                LOGGER.info("Unable to maintain downtime for host '%s': '%s'", host, err)


def set_verification_value(filename, host, setting, value):
    """
    This function stores verification data in a snapshot report. This is done
    by altering the host information dictionary and storing the changes in the
    JSON catalog.

    :param filename: The file to save the information to
    :type filename: str
    :param host: hostname
    :type host: str
    :param setting: setting name
    :type setting: str
    :param value: setting value
    :type value: str
    """
    global REPORT

    host = REPORT[host.hostname]
    host.set_verification(setting, value)
    REPORT[host.hostname] = host

    try:
        write_report(filename, REPORT)
    except IOError as err:
        LOGGER.error("Unable to store report: '%s'", err)
    except ValueError as err:
        LOGGER.error(
            "Unable to set verification setting '%s=%s'", setting, value
        )



def prepare(options, args):
    """
    This function prepares maintenance tasks, which might include creating
    snapshots and scheduling downtime.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #create snapshot/downtime per host
    try:
        for host in REPORT:
            LOGGER.debug("Preparing host '%s'...", host)

            #prepare host
            manage_host_preparation(options, host)

            #verify preparation
            #if not options.generic_dry_run:
                #verify(options, args)

    except ValueError as err:
        LOGGER.error("Error preparing maintenance: '%s'", err)



def execute(options, args):
    """
    This function executes maintenance tasks, which might include applying
    errata.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    try:
        for host in REPORT:
            LOGGER.debug("Patching host '%s'...", host)

            #installing errata
            errata_target = [x["errata_id"] for x in REPORT[host]["errata"]]
            errata_target = [x.encode('utf-8') for x in errata_target]
            if len(errata_target) > 0:
                #errata found
                if options.generic_dry_run:
                    LOGGER.info(
                        "Host '%s' --> install: %s", host, ", ".join(errata_target)
                    )
                else:
                    SAT_CLIENT.api_put(
                        "/hosts/{}/errata/apply".format(
                            SAT_CLIENT.get_id_by_name(host, "host")
                        ),
                        json.dumps({"errata_ids": errata_target})
                    )
            else:
                LOGGER.info("No errata for host %s available", host)

            #install package upgrades
            if options.upgrade_packages:
                if options.generic_dry_run:
                    LOGGER.info(
                        "Host '%s' --> install package upgrades", host
                    )
                else:
                    SAT_CLIENT.api_put(
                        "/hosts/{}/packages/upgrade_all".format(
                            SAT_CLIENT.get_id_by_name(host, "host")
                        ),
                        json.dumps({})
                    )

            #get errata reboot flags
            try:
                errata_reboot = [x["reboot_suggested"] for x in REPORT[host]["errata"]]
            except KeyError:
                #no reboot suggested
                errata_reboot = []
                pass

            if options.foreman_reboot or \
                (True in errata_reboot and not options.foreman_no_reboot):
                if options.generic_dry_run:
                    LOGGER.info("Host '%s' --> reboot host", host)
                else:
                    SAT_CLIENT.api_put(
                        "/hosts/{}/power".format(
                            SAT_CLIENT.get_id_by_name(host, "host")
                        ),
                        json.dumps({"power_action": "soft"})
                    )

    except ValueError as err:
        LOGGER.error("Error maintaining host: '%s'", err)



def revert(options, args):
    """
    This function reverts maintenance tasks.
    As the Foreman APIs lacks possibilities, only VM snapshots are restored
    currently.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #restore snapshots per host
    if options.virt_skip_snapshot:
        return

    snapshots_to_skip = [None, "", "fixmepls"]

    for host in REPORT:
        LOGGER.debug("Restoring host '%s'...", host)

        # create snapshot if applicable
        if host.get_param("katprep_virt_snapshot") in snapshots_to_skip:
            continue

        vm_name = host.virtualisation_id
        snapshot_name = "katprep_{}".format(REPORT_PREFIX)

        try:
            if options.generic_dry_run:
                LOGGER.info(
                    "Host '%s' --> revert snapshot (%s@%s)",
                    host, snapshot_name, vm_name
                )
            else:
                virt_address = host.get_param("katprep_virt")
                virt_client = VIRT_CLIENTS[virt_address]
                virt_client.revert_snapshot(vm_name, snapshot_name)
        except ValueError as err:
            LOGGER.error("Error reverting maintenance: '%s'", err)


def verify(options, args):
    """
    This function verifies maintenance tasks (such as creating snapshots and
    installing errata) and stores status information in a verification log.
    These information are included into host reports by katprep_report.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #verify snapshot/downtime per host
    filename = options.report[0]

    try:
        for host in REPORT:
            LOGGER.debug("Verifying host '%s'...", host)

            #check snapshot
            if not options.virt_skip_snapshot:
                vm_name = host.virtualisation_id
                snapshot_name = "katprep_{}".format(REPORT_PREFIX)

                virt_address = host.get_param("katprep_virt")
                virt_client = VIRT_CLIENTS[virt_address]

                try:
                    if virt_client.has_snapshot(vm_name, snapshot_name):
                        set_verification_value(filename, host, "virt_snapshot", True)
                        LOGGER.info("Snapshot for host '%s' found.", host)
                    else:
                        set_verification_value(filename, host, "virt_cleanup", True)
                        LOGGER.info("No snapshot for host '%s' found, probably cleaned-up.", host)
                except EmptySetException:
                    set_verification_value(filename, host, "virt_cleanup", True)
                    LOGGER.info("No snapshot for host '%s' found, probably cleaned-up.", host)

            #check downtime
            if not options.mon_skip_downtime:
                monitoring_address = host.get_param("katprep_mon")
                monitoring_client = MON_CLIENTS[monitoring_address]

                #check scheduled downtime
                if monitoring_client.has_downtime(host):
                    set_verification_value(filename, host, "mon_downtime", True)
                    LOGGER.info("Downtime for host '%s' found.", host)
                else:
                    #set flag
                    set_verification_value(filename, host, "mon_cleanup", True)
                    LOGGER.info("No downtime for host '%s' found, probably cleaned-up.", host)

                #check critical services
                try:
                    crit_services = monitoring_client.get_services(host)
                except EmptySetException:
                    crit_services = {}

                if len(crit_services) > 0:
                    services = ""
                    LOGGER.debug(
                        "Critical services: '%s'", str(crit_services)
                    )
                    for service in crit_services:
                        services = "{}{} - {}, ".format(
                            services, list(service.keys())[0], list(service.values())[0]
                        )
                    #add status to verfication values
                    set_verification_value(filename, host, "mon_status", "Warning/Critical")
                    set_verification_value(filename, host, "mon_status_detail", services)
                else:
                    set_verification_value(filename, host, "mon_status", "Ok")
                    set_verification_value(filename, host, "mon_status_detail", "All services OK")

    except KeyError:
        #host with either no virt/mon
        pass
        #TODO: seems not to work...
    except ValueError as err:
        LOGGER.error("Error verifying host: '%s'", err)



def status(options, args):
    """
    This function shows current Foreman/Katello software maintenance task
    status.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #verify snapshot/downtime per host
    tasks = {
        "Erratum": "Actions::Katello::Host::Erratum::Install",
        "Package": "Actions::Katello::Host::Update"
    }

    try:
        for host in REPORT:
            LOGGER.debug("Getting '%s' task status...", host)

            #check maintenance progress
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            try:
                for task, task_filter in tasks.items():
                    results = SAT_CLIENT.get_task_by_filter(
                        host, task_filter, today
                    )
                    if results:
                        for result in results:
                            #print result
                            LOGGER.debug(
                                "Found '%s' task %s from %s (state %s)", result["label"],
                                result["id"], result["started_at"], result["result"]
                            )
                            if result["result"].lower() == "success":
                                LOGGER.info(
                                    "%s task for host '%s' succeeded",
                                    task, host
                                )
                            elif result["result"].lower() == "error":
                                LOGGER.info(
                                    "%s task for host '%s' FAILED!",
                                    task, host
                                )
                            else:
                                LOGGER.info(
                                    "%s task for host '%s' has state '%s'",
                                    task, host, result["result"]
                                )
                    else:
                        if task.lower() == "package":
                            LOGGER.info("No %s task for '%s' found!", task.lower(), host)
                        else:
                            LOGGER.error("No %s task for '%s' found!", task.lower(), host)
            except TypeError:
                pass

    except KeyError:
        #host with either no virt/mon
        pass
    except ValueError:
        LOGGER.error("Error getting '%s' task status...", host)


def cleanup(options, args):
    """
    This function cleans things up after executing maintenance tasks. This
    might include removing snapshots and scheduled downtimes.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #remove snapshot/downtime per host
    try:
        for host in REPORT:
            LOGGER.debug("Cleaning-up host '%s'...", host)

            #clean-up host
            manage_host_preparation(options, host, True)

    except ValueError as err:
        LOGGER.error("Error cleaning-up maintenance: '%s'", err)



def load_configuration(config_file, options):
    """
    This function imports parameters and values from a YAML configuration
    file.

    :param config_file: Path to configuration file
    :type config_file: str
    :param options: argparse options dictionary containing the settings
    :type options: argparse options dict
    """
    #try to apply settings from configuration file
    try:
        with open(config_file, 'r') as yml_file:
            config = yaml.load(yml_file)
        #TODO: load configuration
        print("TODO: load_configuration")
    except ValueError as err:
        LOGGER.debug("Error: '%s'", err)
    return options



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for preparing, executing and
    controlling maintenance tasks on systems managed with Foreman/Katello
    or Red Hat Satellite 6.
    You can automatically create snapshots and schedule monitoring downtimes
    if you have set all necessary host parameters using katprep_parameters.
    It is also possible to trigger errata installation using the Foreman API.
    After completing maintenance, it is also possible to remove snapshots and
    downtimes.
    '''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument('--version', action='version', version=__version__)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    fman_opts = parser.add_argument_group("Foreman arguments")
    virt_opts = parser.add_argument_group("virtualization arguments")
    mon_opts = parser.add_argument_group("monitoring arguments")
    filter_opts_excl = fman_opts.add_mutually_exclusive_group()

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", \
    dest="generic_quiet", \
    default=False, help="don't print status messages to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="generic_debug", \
    default=False, action="store_true", \
    help="enable debugging outputs (default: no)")
    #-n / --dry-run
    gen_opts.add_argument("-n", "--dry-run", dest="generic_dry_run", \
    default=False, action="store_true", \
    help="only simulate what would be done (default: no)")
    #-C / --auth-container
    gen_opts.add_argument("-C", "--auth-container", default="", \
    dest="generic_auth_container", action="store", metavar="FILE", \
    help="defines an authentication container file (default: no)")
    #-P / --auth-password
    gen_opts.add_argument("-P", "--auth-password", default="empty", \
    dest="auth_password", action="store", metavar="PASSWORD", \
    help="defines the authentication container password in case you don't " \
    "want to enter it manually (useful for scripted automation)")
    #-c / --config
    gen_opts.add_argument("-c", "--config", dest="config", default="", \
    action="store", metavar="FILE", \
    help="use a configuration rather than 1337 parameters (default: no)")
    #snapshot reports
    gen_opts.add_argument('report', metavar='FILE', nargs=1, \
    help='A snapshot report', type=is_valid_report)
    #--insecure
    gen_opts.add_argument("--insecure", dest="ssl_verify", default=True, \
    action="store_false", help="Disables SSL verification (default: no)")

    #FOREMAN ARGUMENTS
    #-s / --foreman-server
    fman_opts.add_argument("-s", "--foreman-server", \
    dest="foreman_server", metavar="SERVER", default="localhost", \
    help="defines the Foreman server to use (default: localhost)")
    #-r / --reboot-systems
    fman_opts.add_argument("-r", "--reboot-systems", dest="foreman_reboot", \
    default=False, action="store_true", \
    help="always reboot systems after successful errata installation " \
    "(default: no, only if reboot_suggested set)")
    #suppress reboot
    fman_opts.add_argument("-R", "--no-reboot", dest="foreman_no_reboot", \
    default=True, action="store_false", help="suppresses rebooting the " \
    "system under any circumstances (default: no)")

    #VIRTUALIZATION ARGUMENTS
    #--virt-uri
    #TODO: validate URI
    virt_opts.add_argument("--virt-uri", dest="virt_uri", \
    metavar="URI", default="", \
    help="defines a libvirt URI to use")
    #-k / --skip-snapshot
    virt_opts.add_argument("-k", "--skip-snapshot", dest="virt_skip_snapshot", \
    default=False, action="store_true", \
    help="skips creating snapshots (default: no)")

    #MONITORING ARGUMENTS
    #--mon-url
    mon_opts.add_argument("--mon-url", dest="mon_url", \
    metavar="URL", default="", help="defines a monitoring URL to use")
    #--mon-type
    mon_opts.add_argument("--mon-type", dest="mon_type", \
    metavar="TYPE", type=str, choices="nagios|icinga", default="icinga", \
    help="defines the monitoring system type: nagios (Nagios/Icinga 1.x) or" \
    " icinga (Icinga 2.x). (default: icinga)")
    #-K / --skip-downtime
    mon_opts.add_argument("-K", "--skip-downtime", dest="mon_skip_downtime", \
    action="store_true", default=False, \
    help="skips scheduling downtimes (default: no)")
    #-S / --mon-suggested
    mon_opts.add_argument("-S", "--mon-suggested", dest="mon_suggested", \
    action="store_true", default=False, help="only schedules downtime if " \
    "suggested (default: no)")
    #-t / --mon-downtime
    mon_opts.add_argument("-t", "--mon-downtime", dest="mon_downtime", \
    metavar="HOURS", action="store", type=int, default=8, \
    help="downtime period (default: 8 hours)")

    #FILTER ARGUMENTS
    #-l / --location
    filter_opts_excl.add_argument("-l", "--location", action="store", \
    default="", dest="filter_location", metavar="NAME", \
    help="filters by a particular location (default: no)")
    #-o / --organization
    filter_opts_excl.add_argument("-o", "--organization", action="store", \
    default="", dest="filter_organization", metavar="NAME", \
    help="filters by an particular organization (default: no)")
    #-e / --environment
    filter_opts_excl.add_argument("-e", "--environment", action="store", \
    default="", dest="filter_environment", metavar="NAME", \
    help="filters by an particular environment (default: no)")
    #-E / --exclude
    fman_opts.add_argument("-E", "--exclude", action="append", default=[], \
    type=str, dest="filter_exclude", metavar="NAME", \
    help="excludes particular hosts (default: no)")
    #-I / --include-only
    fman_opts.add_argument("-I", "--include-only", action="append", default=[], \
    type=str, dest="filter_include", metavar="NAME", \
    help="only includes particular hosts (default: no)")

    #COMMANDS
    subparsers = parser.add_subparsers(title='commands', \
    description='controlling maintenance stages', help='Additional help')
    cmd_prepare = subparsers.add_parser("prepare", help="Preparing maintenance")
    cmd_prepare.set_defaults(func=prepare)
    cmd_execute = subparsers.add_parser("execute", help="Installing errata")
    cmd_execute.set_defaults(func=execute)
    cmd_execute.add_argument("-p", "--include-packages", action="store_true", \
    default=False, dest="upgrade_packages", help="installs available package" \
    " upgrades (default: no)")
    cmd_status = subparsers.add_parser("status", help="Display software " \
    "maintenance progress")
    cmd_status.set_defaults(func=status)
    cmd_revert = subparsers.add_parser("revert", help="Reverting changes")
    cmd_revert.set_defaults(func=revert)
    cmd_verify = subparsers.add_parser("verify", help="Verifying status")
    cmd_verify.set_defaults(func=verify)
    cmd_cleanup = subparsers.add_parser("cleanup", help="Cleaning-up")
    cmd_cleanup.set_defaults(func=cleanup)

    #parse options and arguments
    options = parser.parse_args()
    #load configuration file
    if options.config != "":
        options = load_configuration(options.config, options)
        options = parser.parse_args()
    #validate hostname
    options.foreman_server = validate_hostname(options.foreman_server)
    #set password
    while options.auth_password == "empty" or len(options.auth_password) > 32:
        options.auth_password = getpass.getpass(
            "Authentication container password: "
        )
    return (options, args)



def set_filter(options, report):
    """
    This function filters a report's hosts by organization, location
    or environment. Also, it evaluates exclude filters.

    :param options: argparse options dictionary containing parameters
    :type options: argparse options dict
    :param report: report data
    :type report: JSON data
    """
    filter_org = options.filter_organization
    filter_location = options.filter_location
    filter_env = options.filter_environment
    filter_exclude = options.filter_exclude
    filter_include = options.filter_include

    remove = []
    for hostname, host in report.items():
        if filter_org and host.organization != filter_org:
            LOGGER.debug("Removing '%s' because of org", hostname)
            remove.append(hostname)
        elif filter_location and host.location != filter_location:
            LOGGER.debug("Removing '%s' because of location", hostname)
            remove.append(hostname)
        elif filter_env and host.get_param("environment_name") != filter_env:
            LOGGER.debug("Removing '%s' because of environment_name", hostname)
            remove.append(hostname)
        elif is_blacklisted(host, filter_exclude):
            LOGGER.debug("Removing '%s' because of exclusion filter", hostname)
            remove.append(hostname)
        elif len(filter_include) > 0 and not is_blacklisted(host, filter_include):
            LOGGER.debug("Removing '%s' because of inclusion filter", hostname)
            remove.append(hostname)

    #remove entries
    for entry in remove:
        del report[entry]

    return report


def main(options, args):
    """Main function, starts the logic based on parameters."""
    global REPORT, REPORT_PREFIX, SAT_CLIENT
    global VIRT_CLIENTS, MON_CLIENTS

    LOGGER.debug("Options: %s", options)
    LOGGER.debug("Arguments: %s", args)

    if options.generic_dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")

    filename = options.report[0]
    REPORT_PREFIX = time.strftime(
        "%Y%m%d", time.gmtime(
            os.path.getmtime(filename)
        )
    )

    REPORT = load_report(filename)
    REPORT = set_filter(options, REPORT)

    #warn if user tends to do something stupid
    if options.virt_skip_snapshot:
        LOGGER.warn("You decided to skip creating snapshots - I've warned you!")
    if options.mon_skip_downtime:
        LOGGER.warn("You decided to skip scheduling downtimes - happy flodding!")

    #initialize APIs
    (fman_user, fman_pass) = get_credentials(
        "Foreman", options.foreman_server, options.generic_auth_container,
        options.auth_password
    )
    SAT_CLIENT = ForemanAPIClient(
        LOG_LEVEL, options.foreman_server, fman_user,
        fman_pass, options.ssl_verify
    )

    #get virtualization host credentials
    if not options.virt_skip_snapshot:
        required_virt = {
            (host.get_param("katprep_virt_type"), host.get_param("katprep_virt"))
            for host in REPORT.values()
            if host.get_param("katprep_virt_type") and host.get_param("katprep_virt")
        }

        for virt_type, virt_address in required_virt:
            virt_prefix = "Virtualization {}".format(virt_address)
            (virt_user, virt_pass) = get_credentials(
                virt_prefix,
                virt_address,
                options.generic_auth_container,
                options.auth_password
            )

            VIRT_CLIENTS[virt_address] = get_virtualization_client(
                virt_type, LOG_LEVEL, virt_address, virt_user, virt_pass)

    #get monitoring host credentials
    if not options.mon_skip_downtime:
        required_mon = {
            (host.get_param("katprep_mon_type"), host.get_param("katprep_mon"))
            for host in REPORT.values()
            if host.get_param("katprep_mon_type") and host.get_param("katprep_mon")
        }

        for monitoring_type, monitoring_address in required_mon:
            (mon_user, mon_pass) = get_credentials(
                "Monitoring {}".format(monitoring_address),
                monitoring_address, options.generic_auth_container, options.auth_password
            )

            MON_CLIENTS[monitoring_address] = get_monitoring_client(monitoring_type, LOG_LEVEL, monitoring_address, mon_user, mon_pass, verify_ssl=options.ssl_verify)

    #start action
    options.func(options, options.func)


def cli():
    """
    This functions initializes the CLI interface
    """

    global LOG_LEVEL
    (options, args) = parse_options()

    #set logging level
    logging.basicConfig()
    if options.generic_debug:
        LOG_LEVEL = logging.DEBUG
    elif options.generic_quiet:
        LOG_LEVEL = logging.ERROR
    else:
        LOG_LEVEL = logging.INFO
    LOGGER.setLevel(LOG_LEVEL)

    main(options, args)



if __name__ == "__main__":
    cli()
