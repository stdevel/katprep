#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
A script which populates the Foreman/Katello or Uyuni host
parameters with information from Nagios/Icinga or a virtualization host
"""

from __future__ import absolute_import

import argparse
import logging
import json
import getpass
from .. import __version__, get_credentials
from ..management import get_management_client
from ..management.foreman import ForemanAPIClient
from ..monitoring import get_monitoring_client
from ..virtualization import get_virtualization_client

LOGGER = logging.getLogger('katprep_populate')
"""
LOGGER: Logger instance
"""
LOG_LEVEL = None
"""
LOG_LEVEL: Logger level
"""
MGMT_CLIENT = None
"""
MGMT_CLIENT: Management client
"""
VIRT_CLIENT = None
"""
VIRT_CLIENT: Virtualization client
"""
MON_CLIENT = None
"""
MON_CLIENT: Monitoring client
"""



def populate(options):
    """
    Retrieves information from a virtualization system and tries to merge
    data with Foreman/Katello.
    """
    LOGGER.info("Gathering host inventory information. " \
        "This *WILL* take some time - please be patient.")
    try:
        #retrieve host information
        hosts = MGMT_CLIENT.get_hosts()
        required_settings = {}

        #retrieve VM/IP information
        if not options.virt_skip:
            vm_hosts = VIRT_CLIENT.get_vm_ips(ipv6_only=options.ipv6_only)
            for host in vm_hosts:
                LOGGER.debug(
                    "HYPERVISOR: Found VM '%s' with IP '%s'",
                    host["hostname"], host["ip"]
                )

        #retrieve monitoring information
        if not options.mon_skip:
            mon_hosts = MON_CLIENT.get_hosts(ipv6_only=options.ipv6_only)
            for host in mon_hosts:
                LOGGER.debug(
                    "MONITORING: Found host '%s' with IP '%s'",
                    host["name"], host["ip"]
                )

        for host in hosts:
            # TODO: make this more generic? useful for re-implementing Foreman support
            _details = MGMT_CLIENT.get_host_details(host)
            _network = MGMT_CLIENT.get_host_network(host)
            _ip = _network["ip6"] if options.ipv6_only else _network["ip"]

            LOGGER.debug(
                "MGMT: Found host '%s' with IP '%s'",
                _details["profile_name"], _ip
            )

            #check if host parameters set appropriately
            required_settings = {}
            try:
                if _ip in [x["ip"] for x in vm_hosts]:
                    LOGGER.debug("Host '%s' is a VM", _details["profile_name"])
                    required_settings["katprep_virt"] = options.virt_uri
                    required_settings["katprep_virt_type"] = options.virt_type
                    vm_name = [x["object_name"] for x in vm_hosts if x["ip"] == _ip]
                    if _details["profile_name"] != vm_name[0]:
                        required_settings["katprep_virt_name"] = vm_name[0]
            except UnboundLocalError:
                pass

            try:
                if _ip in [x["ip"] for x in mon_hosts]:
                    LOGGER.debug("Host '%s' is monitored", _details["profile_name"])

                    required_settings["katprep_mon"] = options.mon_url
                    required_settings["katprep_mon_type"] = options.mon_type
                    mon_name = [x["name"] for x in mon_hosts if x["ip"] == _ip]
                    if _details["profile_name"] != mon_name[0]:
                        required_settings["katprep_mon_name"] = mon_name[0]
            except UnboundLocalError:
                pass

            #set host parameters
            for setting in required_settings:
                if options.generic_dry_run:
                    LOGGER.info(
                        "Host '%s' ==> set/update parameter/value: %s/%s",
                        _details["profile_name"], setting, required_settings[setting]
                    )
                else:
                    # TODO: how to deal with non-existing custom infos?
                    # IDEA: add parameter in katprep_parameters for creating them
                    MGMT_CLIENT.host_add_custom_variable(
                        host, setting, required_settings[setting]
                    )
    except ValueError as err:
        LOGGER.error("Unable to populate virtualization data: '%s'", err)


def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for populating/updating
    Foreman/Katello and Uyuni host parameters with information
    gathered from Nagios, Icinga and Icinga2 and virtualization environments
    accessible via libvirt or pyVmomi (VMware vSphere Python API).
    '''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument('--version', action='version', version=__version__)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    mgmt_opts = parser.add_argument_group("management arguments")
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
    gen_opts.add_argument("-C", "--auth-container", default="", metavar="FILE", \
    dest="generic_auth_container", action="store", help="defines an " \
    "authentication container file (default: no)")
    #-P / --auth-password
    gen_opts.add_argument("-P", "--auth-password", default="empty", \
    dest="auth_password", action="store", metavar="PASSWORD", \
    help="defines the authentication container password in case you don't " \
    "want to enter it manually (useful for scripted automation)")
    #--ip-filter
    gen_opts.add_argument("--ipv6-only", dest="ipv6_only", default=False, \
    action="store_true", help="Filters for IPv6-only addresses (default: no)")
    #--insecure
    gen_opts.add_argument("--insecure", dest="ssl_verify", default=True, \
    action="store_false", help="Disables SSL verification (default: no)")

    #FOREMAN ARGUMENTS
    # --mgmt-type
    mgmt_opts.add_argument(
        "--mgmt-type",
        dest="mgmt_type",
        metavar="foreman|uyuni",
        choices=['foreman', 'uyuni'],
        default="foreman",
        type=str,
        help="defines the library used to operate with management host: "
        "foreman or uyuni (default: foreman)",
    )
    # -s / --server
    mgmt_opts.add_argument(
        "-s",
        "--server",
        dest="server",
        metavar="SERVER",
        default="localhost",
        help="defines the server to use (default: localhost)",
    )
    #-u / --update
    mgmt_opts.add_argument("-u", "--update", dest="foreman_update", \
    action="store_true", default=False, help="Updates pre-existing host " \
    "parameters (default: no)")

    #VIRTUALIZATION ARGUMENTS
    virt_opts.add_argument("--virt-uri", dest="virt_uri", \
    metavar="URI", default="", help="defines an URI to use")
    #--virt-type
    virt_opts.add_argument("--virt-type", dest="virt_type", \
    metavar="libvirt|pyvmomi", default="libvirt", type=str, \
    help="defines the library used to operate with virtualization host: " \
    "libvirt or pyvmomi (vSphere). (default: libvirt)")
    #--skip-virt
    virt_opts.add_argument("--skip-virt", dest="virt_skip", default=False, \
    action="store_true", help="skips gathering data from virtualization " \
    "host (default: no)")

    #MONITORING ARGUMENTS
    #--mon-url
    mon_opts.add_argument("--mon-url", dest="mon_url", \
    metavar="URL", default="", help="defines a monitoring URL to use")
    #--mon-type
    mon_opts.add_argument("--mon-type", dest="mon_type", \
    metavar="nagios|icinga", type=str, choices="nagios|icinga", default="icinga", \
    help="defines the monitoring system type: nagios (Nagios/Icinga 1.x) or" \
    " icinga (Icinga 2.x). (default: icinga)")
    #--skip-mon
    mon_opts.add_argument("--skip-mon", dest="mon_skip", default=False, \
    action="store_true", help="skips gathering data from monitoring system " \
    "(default: no)")

    #parse options and arguments
    options = parser.parse_args()
    while options.auth_password == "empty" or len(options.auth_password) > 32:
        options.auth_password = getpass.getpass(
            "Authentication container password: "
        )
    return (options, args)



def main(options, args):
    """Main function, starts the logic based on parameters."""
    global MGMT_CLIENT, VIRT_CLIENT, MON_CLIENT

    LOGGER.debug("Options: %s", str(options))
    LOGGER.debug("Arguments: %s", str(args))

    if not options.mon_skip and options.mon_url == "":
        LOGGER.error("Please specify a monitoring URL or set --skip-mon")
        exit(1)
    elif not options.virt_skip and options.virt_uri == "":
        LOGGER.error("Please specify a virt URI or set --skip-virt")
        exit(1)
    elif options.mon_skip and options.virt_skip:
        LOGGER.error("Yeah, very funny...")
        exit(1)

    if options.generic_dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")

    #initialize APIs
    (mgmt_user, mgmt_pass) = get_credentials(
        f"Management ({options.mgmt_type})",
        options.server,
        options.generic_auth_container,
        options.auth_password
    )
    MGMT_CLIENT = get_management_client(
        options.mgmt_type,
        LOG_LEVEL,
        mgmt_user,
        mgmt_pass,
        options.server,
        verify=options.ssl_verify,
    )

    #get virtualization host credentials
    if not options.virt_skip:
        (virt_user, virt_pass) = get_credentials(
            "Virtualization", options.virt_uri, options.generic_auth_container,
            options.auth_password
        )

        VIRT_CLIENT = get_virtualization_client(
            options.virt_type, LOG_LEVEL,
            options.virt_uri, virt_user, virt_pass
        )

    #get monitoring host credentials
    if not options.mon_skip:
        (mon_user, mon_pass) = get_credentials(
            "Monitoring", options.mon_url, options.generic_auth_container,
            options.auth_password
        )

        MON_CLIENT = get_monitoring_client(
            options.mon_type, LOG_LEVEL,
            options.mon_url, mon_user, mon_pass,
            verify_ssl=options.ssl_verify
        )

    #populate _all_ the things
    populate(options)



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
