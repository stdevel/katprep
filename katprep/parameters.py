# -*- coding: utf-8 -*-
"""
A script for managing Puppet host parameters for systems managed with
Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import

import argparse
import logging
import json
from . import get_credentials, validate_filters, get_filter
from .clients.ForemanAPIClient import ForemanAPIClient

__version__ = "0.0.1"
"""
str: Program version
"""
LOGGER = logging.getLogger('katprep_parameters')
"""
logging: Logger instance
"""
SAT_CLIENT = None
"""
ForemanAPIClient: Foreman API client handle
"""
PARAMETERS = {
    "katprep_mon" : "Monitoring URL of the system",
    "katprep_virt" : "Virtualization URL of the system",
    "katprep_virt_snapshot" : "Boolean whether system needs to be"\
    " protected by a snapshot before maintenance"}
"""
dict: Built-in default host parameters mandatory for katprep
"""
OPT_PARAMETERS = {
    "katprep_mon_name" : "Object name within moniting if not FQDN",
    "katprep_mon_type" : "Monitoring system type: nagios/(icinga2)",
    "katprep_virt_name": "Object name within hypervisor if not FQDN",
    "katprep_virt_type": "Virtualization host type: (libvirt)/pyvmomi"
}
"""
dict: Built-in optional host parameters
"""
VALUES = {
    "katprep_mon": "fixmepls", "katprep_mon_name": "fixmepls",
    "katprep_virt": "fixmepls", "katprep_virt_snapshot": "0",
    "katprep_virt_name": "fixmepls"}
"""
dict: Default values for built-in host parameters
"""



def list_params():
    """Lists all pre-defined parameters and values."""
    #global parameters

    for key, value in PARAMETERS.items():
        LOGGER.info(
            "Setting '{}' will define '{}'".format(key, value)
        )



def change_param(host, mode="add", dry_run=True):
    """
    Adds/updates/removes parameters for a particular host. For this, a
    host result object and a mode need to be specified.

    :param host: Foreman API result dictionary
    :type host: dict
    :param mode: Mode (add, delete, update)
    :type mode: str
    :param dry_run: Only simulates what woule be done
    :type dry_run: bool
    """
    if mode.lower() == "delete":
        LOGGER.debug("Deleting parameter...")
    elif mode.lower() == "update":
        LOGGER.debug("Updating parameter...")
    else:
        LOGGER.debug("Adding parameter...")

    if options.action_addopt:
        #add optional parameters
        my_params = OPT_PARAMETERS
    else:
        #add mandatory parameters
        my_params = PARAMETERS
    #add _all_ the params
    for param in my_params:
        if dry_run:
            LOGGER.info(
                "Host '{}' (#{}) --> {} parameter '{}'".format(
                    host["name"], host["id"], mode, param
                )
            )
        else:
            #get ID of parameter
            if mode.lower() != "add":
                param_id = SAT_CLIENT.get_hostparam_id_by_name(
                    host["id"], param
                )

            #set payload
            payload = {}
            if mode.lower() == "delete":
                #set parameter ID
                payload["parameter"] = {"id": param_id}
            else:
                #set parameter name/value
                payload["parameter"] = {
                    "name": param, "value": VALUES[param]
                }
            LOGGER.debug(
                "JSON payload: {}".format(json.dumps(payload))
            )

            #send request
            if mode.lower() == "del":
                #delete parameter
                SAT_CLIENT.api_delete(
                    "/hosts/{}/parameters/{}".format(host["id"], param_id),
                    json.dumps(payload))
            elif mode.lower() == "update":
                #update parameter
                SAT_CLIENT.api_put(
                    "/hosts/{}/parameters/{}".format(host["id"], param_id),
                    json.dumps(payload))
            else:
                #add parameter
                SAT_CLIENT.api_post("/hosts/{}/parameters".format(
                    host["id"]
                ), json.dumps(payload))



def manage_params():
    """
    Adds/removes/displays/updates parameter definitions.
    """

    #get all the hosts depending on the filter
    filter_url = get_filter(options, "host")
    LOGGER.debug("Filter URL will be '{}'".format(filter_url))
    result_obj = json.loads(
        SAT_CLIENT.api_get("{}".format(filter_url))
    )

    #manage _all_ the hosts
    for entry in result_obj["results"]:
        LOGGER.debug(
            "Found host '{}' (#{}),".format(entry["name"], entry["id"])
        )
        #execute action
        if options.action_add or options.action_addopt:
            change_param(entry, "add", options.dry_run)
        elif options.action_update:
            change_param(entry, "update", options.dry_run)
        elif options.action_remove:
            change_param(entry, "del", options.dry_run)
        else:
            LOGGER.debug("Displaying parameter values...")

            #display _all_ the params
            params_obj = json.loads(
                SAT_CLIENT.api_get("/hosts/{}/parameters".format(entry["id"]))
            )
            for setting in params_obj["results"]:
                #TODO: nicer way than looping, numpy?
                if "katprep_" in setting["name"]:
                    #warn if default value detected
                    if setting["name"] in PARAMETERS and \
                    setting["value"] == VALUES[setting["name"]]:
                        note = "DEFAULT (!) "
                    else:
                        note = ""
                    LOGGER.info(
                        "Host '{}' (#{}) --> setting '{}' has {}value '{}'"
                        " (created: {} - last updated: {})".format(
                            entry["name"], entry["id"], setting["name"],
                            note, setting["value"], setting["created_at"],
                            setting["updated_at"]
                        )
                    )



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for managing Puppet host parameters
    for systems managed with Foreman/Katello or Red Hat Satellite 6. You can
    create, remove and audit host parameters for all systems. These parameters
    are evaluated by katprep_snapshot to create significant reports.
    Login credentials need to be entered interactively or specified using
    environment variables (SATELLITE_LOGIN, SATELLITE_PASSWORD) or an auth
    container.
    When using an auth container, ensure that the file permissions are 0600 -
    otherwise the script will abort. Maintain the auth container credentials
    with the katprep_authconfig utility.
    '''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(
        description=desc, version=__version__, epilog=epilog
    )

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    srv_opts = parser.add_argument_group("server arguments")
    filter_opts = parser.add_argument_group("filter arguments")
    filter_opts_excl = filter_opts.add_mutually_exclusive_group()
    action_opts = parser.add_argument_group("action arguments")
    action_opts_excl = action_opts.add_mutually_exclusive_group(required=True)

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

    #SERVER ARGUMENTS
    #-C / --auth-container
    gen_opts.add_argument("-C", "--auth-container", default="", \
    dest="auth_container", action="store", help="defines an " \
    "authentication container file (default: no)")
    #-s / --server
    srv_opts.add_argument("-s", "--server", dest="server", metavar="SERVER", \
    default="localhost", help="defines the server to use (default: localhost)")

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

    #ACTION ARGUMENTS
    #-A / --add-parameters
    action_opts_excl.add_argument("-A", "--add-parameters", \
    action="store_true", default=False, dest="action_add", \
    help="adds built-in parameters to all affected hosts (default: no)")
    #--add-optional-parameters
    action_opts_excl.add_argument("--add-optional-parameters", \
    action="store_true", default=False, dest="action_addopt", \
    help="adds optional built-in parameters to all affected hosts (default: no)")
    #-R / --remove-parameters
    action_opts_excl.add_argument("-R", "--remove-parameters", \
    action="store_true", default=False, dest="action_remove", \
    help="removes built-in parameters from all affected hosts (default: no)")
    #-D / --display-values
    action_opts_excl.add_argument("-D", "--display-parameters", \
    action="store_true", default=False, dest="action_display", \
    help="lists values of defined parameters of affected hosts (default: no)")
    #-U / --update-parameters
    action_opts_excl.add_argument("-U", "--update-parameters", \
    action="store_true", default=False, dest="action_update", \
    help="updates values of defined parameters of affected hosts (default: no)")
    #-L / --list-parameters
    action_opts_excl.add_argument("-L", "--list-parameters", \
    action="store_true", default=False, dest="action_list", \
    help="only lists parameters this script uses (default: no)")



    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def main(options):
    """Main function, starts the logic based on parameters."""
    global SAT_CLIENT

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    if options.dry_run:
        LOGGER.info("This is just a SIMULATION - no changes will be made.")

    if options.action_list:
        #only list parameters
        list_params()

    if options.action_update:
        #retrieve values for parameters
        for param in PARAMETERS:
            #prompt for _all_ the parameters
            user_input = ""
            while user_input == "":
                user_input = raw_input(
                    "Enter value for '{}' (hint: {}): ".format(
                        param, PARAMETERS[param]
                    )
                )
            VALUES[param] = user_input

    if not options.action_list:
        #initalize Satellite connection
        (sat_user, sat_pass) = get_credentials(
            "Satellite", options.server, options.auth_container
        )
        SAT_CLIENT = ForemanAPIClient(options.server, sat_user, sat_pass)

        #validate filters
        validate_filters(options, SAT_CLIENT)

        #do the stuff
        manage_params()


def cli():
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
