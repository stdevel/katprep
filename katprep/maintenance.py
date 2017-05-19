# -*- coding: utf-8 -*-
"""
A script which prepares, executes and controls maintenance tasks on systems
managed with Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import

import argparse
import logging
import yaml
import json
import time
import os
from . import is_valid_report, get_json, get_credentials, \
get_required_hosts_by_report, get_host_params_by_report
from .clients.ForemanAPIClient import ForemanAPIClient
from .clients.LibvirtClient import LibvirtClient
from .clients.PyvmomiClient import PyvmomiClient
from .clients.BasicNagiosCGIClient import BasicNagiosCGIClient
from .clients.BasicIcinga2APIClient import BasicIcinga2APIClient

__version__ = "0.0.1"
"""
ForemanAPIClient: Foreman API client handle
"""
LOGGER = logging.getLogger('katprep_maintenance')
"""
logging: Logger instance
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



def get_host_param_from_report(report, host, param):
    """
    This function retrieves a host parameter value from a report.

    :param report: snapshot report data
    :type report: dict
    :param host: hostname
    :type host: str
    :param param: parameter name
    :type param: str
    """
    if param in report[host]["params"] and \
        report[host]["params"][param] != "":
        return report[host]["params"][param]



def manage_host_preparation(options, host, cleanup=False):
    """
    This function prepares or cleans up maintenance tasks for a particular
    host. This includes creating/removing snapshots and scheduled downtimes.

    :param host: hostname
    :type host: str
    :param cleanup: Flag whether preparations should be undone (default: no)
    :type cleanup: bool
    """
    #create snapshot if applicable
    if options.virt_skip_snapshot == False and \
        get_host_param_from_report(REPORT, host, "katprep_virt_snapshot") \
        not in [None, "", "fixmepls"]:
        LOGGER.debug(
            "Host '{}' needs to be protected by a snapshot".format(
                host)
        )
        #use customized VM name if applicable
        if get_host_param_from_report(REPORT, host, "katprep_virt_name") \
            not in ["", None]:
            vm_name = get_host_param_from_report(
                REPORT, host, "katprep_virt_name"
            )
        else:
            vm_name = host

        if options.generic_dry_run:
            if cleanup:
                LOGGER.info(
                    "Host '{}' --> remove snapshot (katprep_{}@{})".format(
                        host, REPORT_PREFIX, vm_name)
                )
            else:
                LOGGER.info(
                    "Host '{}' --> create snapshot (katprep_{}@{})".format(
                        host, REPORT_PREFIX, vm_name)
                )
        else:
            if cleanup:
                #remove snapshot
                VIRT_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_virt")].remove_snapshot(
                    vm_name, "katprep_{}".format(REPORT_PREFIX)
                )
            else:
                #create snapshot
                VIRT_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_virt")].create_snapshot(
                    vm_name, "katprep_{}".format(REPORT_PREFIX),
                    "Snapshot created automatically by katprep"
                )

    #schedule downtime if applicable
    #TODO: only schedule downtime if a patch suggests it?
    if options.mon_skip_downtime == False and \
        get_host_param_from_report(REPORT, host, "katprep_monitoring") \
        not in [None, "", "fixmepls"]:
        LOGGER.debug(
            "Downtime needs to be scheduled for host '{}'".format(
                host)
        )
        #use customized monitoring name if applicable
        if get_host_param_from_report(REPORT, host, "katprep_monitoring_name") \
        not in ["", None]:
            mon_name = get_host_param_from_report(
                REPORT, host, "katprep_monitoring_name"
            )
        else:
            mon_name = host

        if options.generic_dry_run:
            if cleanup:
                LOGGER.info("Host '{}' --> remove downtime".format(host))
            else:
                LOGGER.info("Host '{}' --> schedule downtime".format(host))
        else:
            if cleanup:
                #remove downtime
                MON_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_mon")].remove_downtime(mon_name)
            else:
                #schedule downtime
                MON_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_mon")].schedule_downtime(
                    mon_name, "host", hours=options.mon_downtime
                )



def set_verification_value(options, host, setting, value):
    """
    This function stores verification data in a snapshot report. This is done
    by altering the host information dictionary and storing the changes in the
    JSON catalog.

    :param host: hostname
    :type host: str
    :param setting: setting name
    :type setting: str
    :param value: setting value
    :type value: str
    """
    global REPORT

    try:
        #set value
        REPORT[host]["verification"][setting] = value

        #store file
        with open(options.report[0], 'w') as target:
            target.write(json.dumps(REPORT))
    except IOError as err:
        LOGGER.error("Unable to store report: '{}'".format(err))
    except ValueError as err:
        LOGGER.error(
            "Unable to set verification setting '{}={}'".format(setting, value)
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
            LOGGER.debug("Preparing host '{}'...".format(host))

            #prepare host
            manage_host_preparation(options, host)

            #verify preparation
            if not options.generic_dry_run:
                verify(options, args)

    except ValueError as err:
        LOGGER.error("Error preparing maintenance: '{}'".format(err))



def execute(options, args):
    """
    This function executes maintenance tasks, which might include applying
    errata.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    try:
         for host in REPORT:
            LOGGER.debug("Patching host '{}'...".format(host))
            errata_target = [x["errata_id"] for x in REPORT[host]["errata"]]
            errata_target = [x.encode('utf-8') for x in errata_target]
            if options.generic_dry_run:
                LOGGER.info("Host '{}' --> install: {}".format(
                        host, ", ".join(errata_target)
                    )
                )
            else:
                SAT_CLIENT.api_put(
                    "/hosts/{}/errata/apply".format(
                        SAT_CLIENT.get_id_by_name(host, "host")
                    ),
                    json.dumps({"errata_ids": errata_target})
                )

            if options.foreman_reboot:
                if options.generic_dry_run:
                    LOGGER.info("Host '{}' --> reboot".format(host))
                else:
                    SAT_CLIENT.api_put(
                        "/hosts/{}/power".format(
                            SAT_CLIENT.get_id_by_name(host, "host")
                        ),
                        json.dumps({"power_action": "soft"})
                    )

    except ValueError as err:
        LOGGER.error("Error maintaining host: '{}'".format(err))



def revert(options, args):
    """
    This function reverts maintenance tasks, which might include removing
    errata or restoring virtual machine snapshots.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    print "TODO: implement"



def verify(options, args):
    """
    This function verifies maintenance tasks (such as creating snapshots and
    installing errata) and stores status information in a verification log.
    These information are included into host reports by katprep_report.

    :param args: argparse options dictionary containing parameters
    :type args: argparse options dict
    """
    #verify snapshot/downtime per host
    try:
        for host in REPORT:
            LOGGER.debug("Verifying host '{}'...".format(host))

            #check snapshot
            if not options.virt_skip_snapshot:
                if get_host_param_from_report(
                    REPORT, host, "katprep_virt_name"
                ) not in ["", None]:
                    #customized name
                    vm_name = get_host_param_from_report(
                        REPORT, host, "katprep_virt_name"
                    )
                else:
                    #FQDN
                    vm_name = host
                if VIRT_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_virt")].has_snapshot(
                    vm_name, "katprep_{}".format(REPORT_PREFIX)
                    ):
                    #set flag
                    set_verification_value(options, host, "virt_snapshot", 1)
                    LOGGER.info("Snapshot for host '{}' found.".format(host))
                else:
                    #set flag
                    set_verification_value(options, host, "virt_cleanup", 1)
                    LOGGER.info("No snapshot for host '{}' found, probably cleaned-up.".format(host))

            #check downtime
            if not options.mon_skip_downtime:
                if get_host_param_from_report(
                    REPORT, host, "katprep_monitoring_name"
                ) not in ["", None]:
                    #customized name
                    mon_name = get_host_param_from_report(
                        REPORT, host, "katprep_monitoring_name"
                    )
                else:
                    #FQDN
                    mon_name = host
                #check scheduled downtime
                if MON_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_mon")].has_downtime(mon_name):
                    #set flag
                    set_verification_value(options, host, "mon_downtime", 1)
                    LOGGER.info("Downtime for host '{}' found.".format(host))
                else:
                    #set flag
                    set_verification_value(options, host, "mon_cleanup", 1)
                    LOGGER.info("No downtime for host '{}' found, probably cleaned-up.".format(host))
                #check critical services
                crit_services = MON_CLIENTS[get_host_param_from_report(REPORT, host, "katprep_mon")].get_services(mon_name)
                if len(crit_services) > 0:
                    services = ""
                    for service in crit_services:
                        services = "{}{} - {}, ".format(
                            services, service.keys()[0], service.values()[0]
                        )
                    #add status to verfication values
                    set_verification_value(options, host, "mon_status", "Warning/Critical")
                    set_verification_value(options, host, "mon_status_detail", services)
                else:
                    set_verification_value(options, host, "mon_status", "Ok")

    except KeyError:
        #host with either no virt/mon
        pass
        #TODO: seems not to work...
    except ValueError as err:
        LOGGER.error("Error verifying host: '{}'".format(err))



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
            LOGGER.debug("Cleaning-up host '{}'...".format(host))

            #clean-up host
            manage_host_preparation(options, host, True)

    except ValueError as err:
        LOGGER.error("Error cleaning-up maintenance: '{}'".format(err))



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
        print "TODO: load_configuration"
    except ValueError as err:
        LOGGER.debug("Error: '{}'".format(err))
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
    parser = argparse.ArgumentParser(
        description=desc, version=__version__, epilog=epilog
    )

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
    #-c / --config
    gen_opts.add_argument("-c", "--config", dest="config", default="", \
    action="store", metavar="FILE", \
    help="use a configuration rather than 1337 parameters (default: no)")
    #snapshot reports
    gen_opts.add_argument('report', metavar='FILE', nargs=1, \
    help='A snapshot report', type=is_valid_report)

    #FOREMAN ARGUMENTS
    #-s / --foreman-server
    fman_opts.add_argument("-s", "--foreman-server", \
    dest="foreman_server", metavar="SERVER", default="localhost", \
    help="defines the Foreman server to use (default: localhost)")
    #-r / --reboot-systems
    fman_opts.add_argument("-r", "--reboot-systems", dest="foreman_reboot", \
    default=False, action="store_true", \
    help="reboot systems after successful errata installation (default: no)")
    #--insecure
    fman_opts.add_argument("--insecure", dest="ssl_verify", default=True, \
    action="store_false", help="Disables SSL verification (default: no)")

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

    #COMMANDS
    subparsers = parser.add_subparsers(title='commands', \
    description='controlling maintenance stages', help='additional help')
    cmd_prepare = subparsers.add_parser("prepare", help="Preparing maintenance")
    cmd_prepare.set_defaults(func=prepare)
    cmd_execute = subparsers.add_parser("execute", help="Installing errata")
    cmd_execute.set_defaults(func=execute)
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
    remove = []
    for host in report:
        #removing filtered/blacklisted hosts
        params = report[host]["params"]
        if options.filter_organization != "" and \
            params["organization_name"] != options.filter_organization:
            LOGGER.debug("Removing '{0}'".format(host))
            remove.append(host)
        elif options.filter_location != "" and \
            params["location_name"] != options.filter_location:
            LOGGER.debug("Removing '{0}'".format(host))
            remove.append(host)
        elif options.filter_environment != "" and \
            params["environment_name"] != options.filter_environment:
            LOGGER.debug("Removing '{0}'".format(host))
            remove.append(host)
        elif host in options.filter_exclude:
            LOGGER.debug("Removing '{0}'".format(host))
            remove.append(host)
    #remove entries
    for entry in remove:
        del report[entry]
    return report



def main(options, args):
    """Main function, starts the logic based on parameters."""
    global REPORT, REPORT_PREFIX, SAT_CLIENT
    global VIRT_CLIENTS, MON_CLIENTS

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    if options.generic_dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")

    #load report
    REPORT = json.loads(get_json(options.report[0]))
    REPORT_PREFIX = time.strftime(
        "%Y%m%d", time.gmtime(
            os.path.getmtime(options.report[0])
        )
    )

    #set filter
    REPORT = set_filter(options, REPORT)

    #warn if user tends to do something stupid
    if options.virt_skip_snapshot:
        LOGGER.warn("You decided to skip creating snapshots - I've warned you!")
    if options.mon_skip_downtime:
        LOGGER.warn("You decided to skip scheduling downtimes - happy flodding!")

    #initialize APIs
    (fman_user, fman_pass) = get_credentials(
        "Foreman", options.foreman_server, options.generic_auth_container
    )
    SAT_CLIENT = ForemanAPIClient(
        options.foreman_server, fman_user, fman_pass, options.ssl_verify
    )

    #get virtualization host credentials
    if options.virt_skip_snapshot == False:
        required_virt = get_required_hosts_by_report(REPORT, "katprep_virt")
        for host in required_virt:
            (virt_user, virt_pass) = get_credentials(
                "Virtualization {}".format(host),
                host, options.generic_auth_container
            )
            #create client based on type
            host_params = get_host_params_by_report(REPORT, host)
            if "katprep_virt_type" in host_params and \
                host_params["katprep_virt_type"] == "pyvmomi":
                VIRT_CLIENTS[host] = PyvmomiClient(host, virt_user, virt_pass)
            elif "katprep_virt_type" in host_params:
                VIRT_CLIENTS[host] = LibvirtClient(host, virt_user, virt_pass)

    #get monitoring host credentials
    if options.mon_skip_downtime == False:
        required_mon = get_required_hosts_by_report(REPORT, "katprep_mon")
        for host in required_mon:
            (mon_user, mon_pass) = get_credentials(
                "Monitoring {}".format(host),
                host, options.generic_auth_container
            )
            host_params = get_host_params_by_report(REPORT, host)
            if "katprep_mon_type" in host_params and \
                host_params["katprep_mon_type"] == "nagios":
                #Yet another legacy installation
                MON_CLIENTS[host] = BasicNagiosCGIClient(
                    host, mon_user, mon_pass
                )
            elif "katprep_mon_type" in host_params:
                #Icinga 2, yay!
                MON_CLIENTS[host] = BasicIcinga2APIClient(
                    host, mon_user, mon_pass
                )

    #start action
    options.func(options, options.func)


def cli():
    (options, args) = parse_options()

    #set logging level
    logging.basicConfig()
    if options.generic_debug:
        LOGGER.setLevel(logging.DEBUG)
    elif options.generic_quiet:
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)

    main(options, args)
