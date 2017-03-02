#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script which prepares, executes and controls maintenance tasks on systems
managed with Foreman/Katello or Red Hat Satellite 6.
"""

import argparse
import logging
#import json
#from katprep_shared import get_credentials, ForemanAPIClient, \
#validate_filters, get_filter

__version__ = "0.0.1"
LOGGER = logging.getLogger('katprep_maintenance')
SAT_CLIENT = None



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''katprep_maintenace.py is used for preparing, executing and
    controlling maintenance tasks on systems managed with Foreman/Katello
    or Red Hat Satellite 6.
    You can automatically create snapshots and schedule monitoring downtimes
    if you have set all necessary host parameters using katprep_parameters.py.
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
    gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", \
    default=False, help="don't print status messages to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="debug", default=False, \
    action="store_true", help="enable debugging outputs (default: no)")
    #-n / --dry-run
    gen_opts.add_argument("-n", "--dry-run", dest="dry_run", default=False, \
    action="store_true", help="only simulate what would be done (default: no)")
    #-c / --config
    gen_opts.add_argument("-c", "--config", dest="config", default="", \
    action="store", metavar="FILE", type=argparse.FileType('r'), \
    help="use a configuration rather than 1337 parameters (default: no)")

    #FOREMAN ARGUMENTS
    #-a / --foreman-authfile
    fman_opts.add_argument("-a", "--foreman-authfile", dest="fman_authfile", \
    metavar="FILE", default="", \
    help="defines an auth file to use instead of shell variables")
    #-s / --foreman-server
    fman_opts.add_argument("-s", "--foreman-server", dest="fman_server", \
    metavar="SERVER", default="localhost", \
    help="defines the Foreman server to use (default: localhost)")

    #VIRTUALIZATION ARGUMENTS
    #--virtualization-authfile
    virt_opts.add_argument("--virtualization-authfile", dest="virt_authfile", \
    metavar="FILE", default="", \
    help="defines an auth file to use instead of shell variables")
    #--virtualization-server
    virt_opts.add_argument("--virtualization-server", dest="virt_server", \
    metavar="SERVER", default="", \
    help="defines a virtualization resource to use")
    #-k / --skip-snapshot
    virt_opts.add_argument("-k", "--skip-snapshot", dest="virt_skip_snapshot", \
    default=False, action="store_true", \
    help="skips creating snapshots (default: no)")

    #MONITORING ARGUMENTS
    #--monitoring-authfile
    mon_opts.add_argument("--monitoring-authfile", dest="mon_authfile", \
    metavar="FILE", default="", \
    help="defines an auth file to use instead of shell variables")
    #--monitoring-server
    mon_opts.add_argument("--monitoring-server", dest="mon_server", \
    metavar="SERVER", default="", help="defines a monitoring host to use")
    #-K / --skip-monitoring
    mon_opts.add_argument("-K", "--skip-monitoring", dest="mon_skip_downtime", \
    action="store_true", default=False, \
    help="skips scheduling downtimes (default: no)")

    #FILTER ARGUMENTS
    #-l / --location
    filter_opts_excl.add_argument("-l", "--location", action="store", \
    default="", dest="location", metavar="NAME|ID", \
    help="filters by a particular location (default: no)")
    #-o / --organization
    filter_opts_excl.add_argument("-o", "--organization", action="store", \
    default="", dest="organization", metavar="NAME|ID", \
    help="filters by an particular organization (default: no)")
    #-g / --hostgroup
    filter_opts_excl.add_argument("-g", "--hostgroup", action="store", \
    default="", dest="hostgroup", metavar="NAME|ID", \
    help="filters by a particular hostgroup (default: no)")
    #-e / --environment
    filter_opts_excl.add_argument("-e", "--environment", action="store", \
    default="", dest="environment", metavar="NAME|ID", \
    help="filters by an particular environment (default: no)")

    #COMMANDS
    subparsers = parser.add_subparsers(title='commands', \
    description='controlling maintenance stages', help='additional help')

    #prepare
    subparsers.add_parser("prepare", help="Preparing maintenace")
    subparsers.add_parser("execute", help="Installing errata")
    subparsers.add_parser("verify", help="Verifying status")
    subparsers.add_parser("cleanup", help="Cleaning-up")



    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def main(options):
    """Main function, starts the logic based on parameters."""
    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    if options.dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")



if __name__ == "__main__":
    (options, args) = parse_options()

    #set logging level
    logging.basicConfig()
    if options.debug:
        LOGGER.setLevel(logging.DEBUG)
    elif options.quiet:
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)

    main(options)
