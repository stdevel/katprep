#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script for creating a snapshot report of available errata and updates for
systems managed with Foreman/Katello or Red Hat Satellite 6.
"""

import argparse
import logging
import json
import time
from katprep_shared import get_credentials, is_writable, validate_filters, \
get_filter
from ForemanAPIClient import ForemanAPIClient

__version__ = "0.0.1"
"""
str: Program version
"""
LOGGER = logging.getLogger('katprep_snapshot')
"""
logging: Logger instance
"""
SAT_CLIENT = None
"""
ForemanAPIClient: Foreman API client handle
"""
SYSTEM_ERRATA = {}
"""
dict: Errata and parameter information per system
"""
OUTPUT_FILE = ""
"""
str: Output file
"""



def parse_options(args=None):
    """Parses options and arguments."""

    desc = '''katprep_snapshot.py is used for creating snapshot reports of
    errata available to your systems managed with Foreman/Katello or Red
    Hat Satellite 6. You can use two snapshot reports to create delta
    reports using katprep_report.py.
    Login credentials need to be entered interactively or specified using
    environment variables (SATELLITE_LOGIN, SATELLITE_PASSWORD) or an authfile.
    When using an authfile, ensure that the file permissions are 0600 - 
    otherwise the script will abort. The first line needs to contain the
    username, the second line represents the appropriate password.
    '''
    epilog = '''Check-out the website for more details:
http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(description=desc, version=__version__, \
    epilog=epilog)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    srv_opts = parser.add_argument_group("server arguments")
    filter_opts = parser.add_argument_group("filter arguments")
    filter_opts_excl = filter_opts.add_mutually_exclusive_group()

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", \
    default=False, help="don't print status messages to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="debug", default=False, \
    action="store_true", help="enable debugging outputs (default: no)")
    #-p / --output-path
    gen_opts.add_argument("-p", "--output-path", dest="output_path", \
    metavar="PATH", default="", action="store", help="defines the output path" \
    " for reports (default: current directory)")

    #SERVER ARGUMENTS
    #-a / --authfile
    srv_opts.add_argument("-a", "--authfile", dest="authfile", metavar="FILE", \
    default="", help="defines an auth file to use instead of shell variables")
    #-s / --server
    srv_opts.add_argument("-s", "--server", dest="server", metavar="SERVER", \
    default="localhost", help="defines the server to use (default: localhost)")

    #SNAPSHOT FILTER ARGUMENTS
    #-l / --location
    filter_opts_excl.add_argument("-l", "--location", action="store", \
    default="", dest="location", metavar="NAME|ID", help="filters by a" \
    " particular location (default: no)")
    #-o / --organization
    filter_opts_excl.add_argument("-o", "--organization", action="store", \
    default="", dest="organization", metavar="NAME|ID", help="filters by an" \
    " particular organization (default: no)")
    #-g / --hostgroup
    filter_opts_excl.add_argument("-g", "--hostgroup", action="store", \
    default="", dest="hostgroup", metavar="NAME|ID", help="filters by a" \
    " particular hostgroup (default: no)")
    #-e / --environment
    filter_opts_excl.add_argument("-e", "--environment", action="store", \
    default="", dest="environment", metavar="NAME|ID", help="filters by an" \
    " particular environment (default: no)")



    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def scan_systems():
    """Scans all systems that were selected for errata counters."""

    try:
        #get all the hosts depending on the filter
        filter_url = get_filter(options, "host")
        LOGGER.debug("Filter URL will be '{}'".format(filter_url))
        result_obj = json.loads(
            SAT_CLIENT.api_get("{}".format(filter_url))
        )

        #get errata per system
        for system in result_obj["results"]:
            LOGGER.info("Checking system '{}' (#{})...".format(system["name"], \
            system["id"]))
            LOGGER.debug("System errata counter: security={}, bugfix={}," \
            " enhancement={}, total={}".format(
                system["content_facet_attributes"]["errata_counts"]["security"],
                system["content_facet_attributes"]["errata_counts"]["bugfix"],
                system["content_facet_attributes"]["errata_counts"]["enhancement"],
                system["content_facet_attributes"]["errata_counts"]["total"]
            ))
            if int(system["content_facet_attributes"]["errata_counts"]["total"]) > 0:
                #errata applicable
                SYSTEM_ERRATA[system["name"]] = {}
                SYSTEM_ERRATA[system["name"]]["params"] = {}
                SYSTEM_ERRATA[system["name"]]["verification"] = {}
                SYSTEM_ERRATA[system["name"]]["errata"] = {}
                result_obj = json.loads(
                    SAT_CLIENT.api_get("/hosts/{}/errata".format(system["id"]))
                )
                #add _all_ the katprep_* params
                params_obj = json.loads(
                    SAT_CLIENT.api_get("/hosts/{}".format(system["id"]))
                )
                for entry in params_obj["parameters"]:
                    if "katprep_" in entry["name"]:
                        #add key/value
                        SYSTEM_ERRATA[system["name"]]["params"][entry["name"]] = {}
                        SYSTEM_ERRATA[system["name"]]["params"][entry["name"]] = entry["value"]
                #add some additional information required for katprep_report
                SYSTEM_ERRATA[system["name"]]["params"]["name"] = params_obj["name"]
                SYSTEM_ERRATA[system["name"]]["params"]["ip"] = params_obj["ip"]
                SYSTEM_ERRATA[system["name"]]["params"]["owner"] =  \
                    SAT_CLIENT.get_name_by_id(params_obj["owner_id"], "user")
                SYSTEM_ERRATA[system["name"]]["params"]["organization"] = params_obj["organization_name"]
                SYSTEM_ERRATA[system["name"]]["params"]["location"] = params_obj["location_name"]
                SYSTEM_ERRATA[system["name"]]["params"]["environment"] = params_obj["environment_name"]
                SYSTEM_ERRATA[system["name"]]["params"]["operatingsystem"] = params_obj["operatingsystem_name"]
                if params_obj["facts"]["virt::is_guest"] == True:
                    SYSTEM_ERRATA[system["name"]]["params"]["system_physical"] = False
                else:
                    SYSTEM_ERRATA[system["name"]]["params"]["system_physical"] = True
                #add _all_ the errata information
                SYSTEM_ERRATA[system["name"]]["errata"] = result_obj["results"]
    except KeyError as err:
        LOGGER.error("Unable to get system information, check filter options!")
    except ValueError as err:
        LOGGER.info("Unable to get data: '{}'".format(err))



def create_report():
    """Creates a JSON report including errata information of all hosts."""

    try:
        target = open(OUTPUT_FILE, 'w')
        target.write(
            json.dumps(SYSTEM_ERRATA)
        )
        target.close()
    except IOError as err:
        LOGGER.error("Unable to store report: '{}'".format(err))
    else:
        LOGGER.info("Report '{}' created.".format(OUTPUT_FILE))



def main(options):
    """Main function, starts the logic based on parameters."""
    global SAT_CLIENT, OUTPUT_FILE

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    #set output file
    if options.output_path == "":
        options.output_path = "./"
    elif options.output_path != "" and \
    options.output_path[len(options.output_path)-1:] != "/":
        #add trailing slash
        options.output_path = "{}/".format(options.output_path)
    OUTPUT_FILE = "{}errata-snapshot-report-{}-{}.json".format(
        options.output_path,
        options.server.split('.')[0],
        time.strftime("%Y%m%d-%H%M")
    )
    LOGGER.debug("Output file will be: '{}'".format(OUTPUT_FILE))

    #check if we can read and write before digging
    if is_writable(OUTPUT_FILE):
        #initalize Satellite connection and scan systems
        (sat_user, sat_pass) = get_credentials("Satellite", options.authfile)
        SAT_CLIENT = ForemanAPIClient(options.server, sat_user, sat_pass)

        #validate filters
        validate_filters(options, SAT_CLIENT)

        #scan systems and create report
        scan_systems()
        create_report()
    else:
        LOGGER.error("Directory '{}' is not writable!".format(OUTPUT_FILE))



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
