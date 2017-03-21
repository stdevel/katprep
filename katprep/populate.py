# -*- coding: utf-8 -*-
"""
A script which populates the Foreman/Katello or Red Hat Satellite 6 host
parameters with information from Nagios/Icinga or a virtualization host
"""

from __future__ import absolute_import

import argparse
import logging
import yaml
import json
import time
import os
from . import is_valid_report, get_json, get_credentials, \
get_required_hosts_by_report
from .clients.ForemanAPIClient import ForemanAPIClient
from .clients.LibvirtClient import LibvirtClient
from .clients.PyvmomiClient import PyvmomiClient
from .clients.BasicNagiosCGIClient import BasicNagiosCGIClient
from .clients.BasicIcinga2APIClient import BasicIcinga2APIClient

__version__ = "0.0.1"
"""
ForemanAPIClient: Foreman API client handle
"""
LOGGER = logging.getLogger('katprep_populate')
"""
logging: Logger instance
"""
SAT_CLIENT = None
"""
ForemanAPIClient: Foreman API client handle
"""
VIRT_CLIENT = None
"""
LibvirtClient: libvirt API client handle
"""
MON_CLIENT = None
"""
BasicNagiosCGIClient: Nagios CGI client handle
"""



def populate_virt():
    """
    Retrieves information from a virtualization system and tries to merge
    data with Foreman/Katello.
    """
    try:
        #retrieve VM/IP information
        vm_hosts = VIRT_CLIENT.list_vm_hosts()
        #retrieve host information
        hosts = params_obj = json.loads(SAT_CLIENT.api_get("/hosts"))
        #required settings
        required_settings = {
            "katprep_virt": options.virt_uri,
            "katprep_virt_type": options.virt_type
        }

        #check _all_ the hosts
        for host in hosts["results"]:
            #check if katprep_virt_type and katprep_virt is set appropriate
            #if
            print "TODO"

        #for vm in vm_ips:
            #LOGGER.debug(
                #"Found VM '{}' with IP '{}'".format(vm, vm_ips[vm]["ip"])
            #)
    except ValueError as err:
        LOGGER.error("Unable to populate virtualization data: '{}'".format(err))



def populate_mon():
    """
    Retrieves information from a monitoring system and tries to merge data
    with Foreman/Katello.
    """
    print "TODO: populate_mon"



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for populating/updating
    Foreman/Katello and Red Hat Satellite 6 host parameters with information
    gathered from Nagios, Icinga and Icinga2 and virtualization environments
    accessible via libvirt or pyVmomi (VMware vSphere Python API).
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

    #FOREMAN ARGUMENTS
    #-s / --foreman-server
    fman_opts.add_argument("-s", "--foreman-server", \
    dest="foreman_server", metavar="SERVER", default="localhost", \
    help="defines the Foreman server to use (default: localhost)")

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
    metavar="TYPE", type=str, choices="nagios|icinga", default="icinga", \
    help="defines the monitoring system type: nagios (Nagios/Icinga 1.x) or" \
    " icinga (Icinga 2.x). (default: icinga)")
    #--skip-mon
    mon_opts.add_argument("--skip-mon", dest="mon_skip", default=False, \
    action="store_true", help="skips gathering data from monitoring system " \
    "(default: no)")

    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def main(options, args):
    """Main function, starts the logic based on parameters."""
    global SAT_CLIENT, VIRT_CLIENT, MON_CLIENT

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    if not options.mon_skip and options.mon_url == "":
        LOGGER.error("Please specify a monitoring URL or set --skip-mon")
        exit(1)
    elif not options.virt_skip and options.virt_uri == "":
        LOGGER.error("Please specify a virt URI or set --skip-virt")
        exit(1)

    if options.generic_dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")

    #initialize APIs
    (fman_user, fman_pass) = get_credentials(
        "Foreman", options.foreman_server, options.generic_auth_container
    )
    SAT_CLIENT = ForemanAPIClient(options.foreman_server, fman_user, fman_pass)

    #get virtualization host credentials
    if options.virt_skip == False:
        (virt_user, virt_pass) = get_credentials(
            "Virtualization", options.virt_uri, options.generic_auth_container
        )
        if options.virt_type == "pyvmomi":
            #vSphere Python API
            VIRT_CLIENT = PyvmomiClient(options.virt_uri, virt_user, virt_pass)
        else:
            #libvirt
            VIRT_CLIENT = LibvirtClient(options.virt_uri, virt_user, virt_pass)
        #populate from virtualization host
        populate_virt()

    #get monitoring host credentials
    if options.mon_skip == False:
        (mon_user, mon_pass) = get_credentials(
            "Monitoring", options.mon_url, options.generic_auth_container
        )
        if options.mon_type == "nagios":
            #Yet another legacy installation
            MON_CLIENT = BasicNagiosCGIClient(
                options.mon_url, mon_user, mon_pass
            )
        else:
            #Icinga 2, yay!
            MON_CLIENT = BasicIcinga2APIClient(
                options.mon_url, mon_user, mon_pass
            )
        #populate from monitoring host
        populate_mon()


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
