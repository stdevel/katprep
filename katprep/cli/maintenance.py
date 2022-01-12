#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
Prepare, execute and control maintenance tasks.
"""

import argparse
import datetime
import getpass
import logging
import os
import time
import yaml

from .. import __version__, get_credentials
from ..exceptions import (
    EmptySetException, InvalidCredentialsException,
    SessionException, SnapshotExistsException, UnsupportedRequestException
    )
from ..management import get_management_client
from ..monitoring import get_monitoring_client
from ..network import validate_hostname
from ..reports import is_valid_report, load_report, write_report
from ..virtualization import get_virtualization_client

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
SAT_CLIENT: Management client
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
SNAPSHOTS_TO_SKIP = {None, "", "fixmepls"}
"""
set([str, ]): Snapshot names that will be skipped
"""


def is_blacklisted(host: str, blacklist: list):
    """
    This function checks whether a host is matched by an exclude pattern.

    :param host: Hostname
    :type host: str
    :param blacklist: List of blacklisted terms
    :type blacklist: [str, ]
    """
    return any(entry in host for entry in blacklist)


def manage_host_preparation(options, host, cleanup=False):
    """
    This function prepares or cleans up maintenance tasks for a particular
    host. This includes creating/removing snapshots and scheduled downtimes.

    :param host: host object to work with
    :type host: Host
    :param cleanup: Flag whether preparations should be undone (default: no)
    :type cleanup: bool
    """
    snapshot = host.get_param("katprep_virt_snapshot")

    #create snapshot if applicable
    if not options.virt_skip_snapshot and snapshot not in SNAPSHOTS_TO_SKIP:
        LOGGER.debug(
            "Host '%s' needs to be protected by a snapshot", host
        )

        vm_name = host.virtualisation_id
        snapshot_name = "katprep_{}".format(REPORT_PREFIX)

        virt_address = host.get_param("katprep_virt")
        virt_client = VIRT_CLIENTS[virt_address]

        try:
            if cleanup:  # remove snapshot
                LOGGER.info(
                    "Host '%s' --> remove snapshot (%s@%s)",
                    host, snapshot_name, vm_name
                )

                if not options.generic_dry_run:
                    virt_client.remove_snapshot(host, snapshot_name)
            else:  # create snapshot
                LOGGER.info(
                    "Host '%s' --> create snapshot (%s@%s)",
                    host, snapshot_name, vm_name
                )

                if not options.generic_dry_run:
                    virt_client.create_snapshot(
                        host, snapshot_name,
                        "Snapshot created automatically by katprep"
                    )
        except InvalidCredentialsException as err:
            LOGGER.error("Invalid crendentials supplied")
        except SnapshotExistsException as err:
            LOGGER.info("Snapshot for host '%s' already exists: %s", host.hostname, err)
        except EmptySetException as err:
            LOGGER.info("Snapshot for host '%s' already removed: %s", host.hostname, err)
        except SessionException as err:
            LOGGER.exception(err)
            LOGGER.error("Unable to manage snapshot for host '%s': %s", host.hostname, err)

    errata_reboot = SAT_CLIENT.is_reboot_required(host)

    #schedule downtime if applicable
    #TODO: only schedule downtime if a patch suggests it?
    if options.mon_skip_downtime:
        return

    monitoring_address = host.get_param("katprep_mon")
    unwanted_monitoring_addresss = [None, "", "fixmepls"]

    if monitoring_address not in unwanted_monitoring_addresss or \
        (options.mon_suggested and errata_reboot):

        LOGGER.debug(
            "Downtime needs to be scheduled for host '%s'", host
        )

        monitoring_client = MON_CLIENTS[monitoring_address]
        try:
            if cleanup:
                LOGGER.info("Host '%s' --> remove downtime", host.hostname)

                if not options.generic_dry_run:
                    monitoring_client.remove_downtime(host)
            else:
                LOGGER.info("Host '%s' --> schedule downtime", host.hostname)

                if not options.generic_dry_run:
                    monitoring_client.schedule_downtime(host,
                                                        hours=options.mon_downtime)
        except InvalidCredentialsException as err:
            LOGGER.error("Unable to maintain downtime: '%s'", err)
        except UnsupportedRequestException as err:
            LOGGER.info("Unable to maintain downtime for host '%s': '%s'", host.hostname, err)


def set_verification_value(filename, host, setting, value):
    """
    This function stores verification data in a snapshot report. This is done
    by altering the host information dictionary and storing the changes in the
    JSON catalog.

    :param filename: The file to save the information to
    :type filename: str
    :param host: Host to alter
    :type host: Host
    :param setting: setting name
    :type setting: str
    :param value: setting value
    :type value: str
    """
    global REPORT

    # explicit conversion to str as JSON requires keys to be strings ¯\_(ツ)_/¯
    management_id = str(host.management_id)
    host = REPORT[management_id]
    host.set_verification(setting, value)
    REPORT[management_id] = host

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
    try:
        for host in REPORT.values():
            LOGGER.debug("Preparing host '%s'...", host)
            manage_host_preparation(options, host)

            # verify preparation
            # if not options.generic_dry_run:
            #   verify(options, args)
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
        for host_obj in REPORT.values():
            LOGGER.debug("Patching host '%s'...", host_obj)

            _install_erratas(host_obj, options.generic_dry_run)

            if options.upgrade_packages:
                _install_package_upgrades(host_obj, options.generic_dry_run)

            reboot_wanted = SAT_CLIENT.is_reboot_required(host_obj)
            if options.mgmt_reboot or \
                (reboot_wanted and not options.mgmt_no_reboot):

                LOGGER.info("Host '%s' --> reboot host", host_obj)
                if not options.generic_dry_run:
                    SAT_CLIENT.reboot_host(host_obj)
    except ValueError as err:
        LOGGER.error("Error maintaining host: '%s'", err)


def _install_erratas(host, dry_run):
    LOGGER.debug("Erratas of the host %s: %s", host, host.patches)
    if host.patches:
        patch_ids = [str(errata.id) for errata in host.patches]
        LOGGER.info(
            "Host '%s' --> installing %i patches: %s", host, len(host.patches), ", ".join(patch_ids)
        )

        if not dry_run:
            SAT_CLIENT.install_patches(host)
    else:
        LOGGER.info("No errata for host %s available", host)


def _install_package_upgrades(host, dry_run):
    LOGGER.info(
        "Host '%s' --> install package upgrades", host
    )

    if not dry_run:
        SAT_CLIENT.install_upgrades(host)


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

    for host in REPORT.values():
        LOGGER.debug("Restoring host '%s'...", host)

        # create snapshot if applicable
        if host.get_param("katprep_virt_snapshot") in SNAPSHOTS_TO_SKIP:
            continue

        vm_name = host.virtualisation_id
        snapshot_name = "katprep_{}".format(REPORT_PREFIX)

        try:
            LOGGER.info(
                "Host '%s' --> revert snapshot (%s@%s)",
                host, snapshot_name, vm_name
            )

            if not options.generic_dry_run:
                virt_address = host.get_param("katprep_virt")
                virt_client = VIRT_CLIENTS[virt_address]
                virt_client.revert_snapshot(host, snapshot_name)
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
        for host_id, host in REPORT.items():
            LOGGER.debug("Verifying host '%s'...", host)

            #check snapshot
            if not options.virt_skip_snapshot:
                vm_name = host.virtualisation_id
                snapshot_name = "katprep_{}".format(REPORT_PREFIX)

                virt_address = host.get_param("katprep_virt")
                if virt_address:
                    virt_client = VIRT_CLIENTS[virt_address]
                    try:
                        if virt_client.has_snapshot(host, snapshot_name):
                            LOGGER.info("Snapshot for host '%s' found.", host)
                            set_verification_value(filename, host, "virt_snapshot", True)
                        else:
                            LOGGER.info(
                                "No snapshot for host '%s' found, probably cleaned-up.", host
                            )
                            set_verification_value(filename, host, "virt_cleanup", True)
                    except EmptySetException:
                        LOGGER.info("No snapshot for host '%s' found, probably cleaned-up.", host)
                        set_verification_value(filename, host, "virt_cleanup", True)
                else:
                    LOGGER.info("Host '%s' is not a VM", host)

            #check downtime
            if not options.mon_skip_downtime:
                monitoring_address = host.get_param("katprep_mon")
                if monitoring_address is None:
                    LOGGER.info("Monitoring for host '%s' not configured", host)
                    continue

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

    except ValueError as err:
        LOGGER.error("Error verifying host: '%s'", err)


def status(options, args):
    """
    This function shows current Foreman/Katello software maintenance task
    status.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    for host_id, host in REPORT.items():
        LOGGER.debug("Getting '%s' task status...", host)
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # filter for errata/upgrade tasks from today
        errata_tasks = SAT_CLIENT.get_errata_task_status(int(host_id))
        errata_tasks = [x for x in errata_tasks if today in x['created']]
        upgrade_tasks = SAT_CLIENT.get_upgrade_task_status(int(host_id))
        upgrade_tasks = [x for x in upgrade_tasks if today in x['created']]
        LOGGER.debug("Erratas for host '%s': %s", int(host_id), len(errata_tasks))
        LOGGER.debug("Upgrades for host '%s': %s", int(host_id), len(upgrade_tasks))

        # check all the tasks
        _tasks = errata_tasks + upgrade_tasks
        for _task in _tasks:

            # TODO: We might need to change keys/adopt format
            # when re-implementing Foreman support
            if _task["successful_count"] != 0:
                LOGGER.info(
                    "%s task for host '%s' succeeded",
                    _task['name'], host
                )
            elif _task["failed_count"] != 0:
                LOGGER.info(
                    "%s task for host '%s' FAILED!",
                    _task['name'], host
                )
            else:
                LOGGER.info(
                    "%s task for host '%s' still running...",
                    _task['name'], host
                )


def cleanup(options, args):
    """
    This function cleans things up after executing maintenance tasks.
    This might include removing snapshots and scheduled downtimes.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    try:
        for host_id, host in REPORT.items():
            LOGGER.debug("Cleaning-up host '%s'...", host_id)
            manage_host_preparation(options, host, cleanup=True)
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
    raise NotImplementedError("Loading a configuration from a file is currently not implemented.")

    #try to apply settings from configuration file
    try:
        with open(config_file, 'r') as yml_file:
            config = yaml.load(yml_file)
        #TODO: load configuration
    except ValueError as err:
        LOGGER.debug("Error: '%s'", err)
    return options


def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for preparing, executing and
    controlling maintenance tasks.

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
    mgmt_opts = parser.add_argument_group("Management system arguments")
    virt_opts = parser.add_argument_group("virtualization arguments")
    mon_opts = parser.add_argument_group("monitoring arguments")

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

    # MANAGEMENT ARGUMENTS
    mgmt_opts.add_argument(
        "--mgmt-type",
        dest="mgmt_type",
        metavar="foreman|uyuni",
        choices=["foreman", "uyuni"],
        default="foreman",
        type=str,
        help="defines the library used to operate with management host: "
        "foreman or uyuni (default: foreman)",
    )
    mgmt_opts.add_argument("-s", "--mgmt-server", \
    dest="mgmt_server", metavar="SERVER", default="localhost", \
    help="defines the management server to use (default: localhost)")
    mgmt_opts.add_argument("-r", "--reboot-systems", dest="mgmt_reboot", \
    default=False, action="store_true", \
    help="always reboot systems after successful errata installation " \
    "(default: no, only if reboot_suggested set)")
    mgmt_opts.add_argument("-R", "--no-reboot", dest="mgmt_no_reboot", \
    default=True, action="store_false", help="suppresses rebooting the " \
    "system under any circumstances (default: no)")

    #VIRTUALIZATION ARGUMENTS
    #--virt-uri
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
    metavar="TYPE", type=str, choices="nagios|icinga|icinga2", default="icinga2", \
    help="defines the monitoring system type: nagios, icinga (Icinga 1.x) or" \
    " icinga2 (Icinga 2.x). (default: icinga2)")
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
    filter_opts_excl = mgmt_opts.add_mutually_exclusive_group()
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
    filter_opts_excl.add_argument("-E", "--exclude", action="append", default=[], \
    type=str, dest="filter_exclude", metavar="NAME", \
    help="excludes particular hosts (default: no)")
    #-I / --include-only
    filter_opts_excl.add_argument("-I", "--include-only", action="append", default=[], \
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
    if options.config:
        options = load_configuration(options.config, options)
        options = parser.parse_args()

    options.mgmt_server = validate_hostname(options.mgmt_server)
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
    def prepare_filter_list(blacklist):
        return [entry.replace("*", "").replace("%", "") for entry in blacklist]

    filter_org = options.filter_organization
    filter_location = options.filter_location
    filter_env = options.filter_environment
    filter_exclude = prepare_filter_list(options.filter_exclude)
    filter_include = prepare_filter_list(options.filter_include)

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
        elif is_blacklisted(hostname, filter_exclude):
            LOGGER.debug("Removing '%s' because of exclusion filter", hostname)
            remove.append(hostname)
        elif len(filter_include) > 0 and not is_blacklisted(hostname, filter_include):
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
        LOGGER.warning("You decided to skip creating snapshots - I've warned you!")
    if options.mon_skip_downtime:
        LOGGER.warning("You decided to skip scheduling downtimes - happy flodding!")

    #initialize APIs
    (management_user, management_password) = get_credentials(
        f"Management ({options.mgmt_type})", options.mgmt_server, options.generic_auth_container,
        options.auth_password
    )

    SAT_CLIENT = get_management_client(
        options.mgmt_type, LOG_LEVEL,
        management_user, management_password, options.mgmt_server,
        verify=options.ssl_verify
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
        # TODO: use icinga2 by default if not defined?
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

            MON_CLIENTS[monitoring_address] = get_monitoring_client(
                monitoring_type,
                LOG_LEVEL,
                monitoring_address,
                mon_user, mon_pass,
                verify_ssl=options.ssl_verify
            )

    #start action
    if not hasattr(options, 'func'):
        raise ValueError("Please select an action you want to perform!")
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
