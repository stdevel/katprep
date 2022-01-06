#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
A script for managing Puppet host parameters for systems managed with
Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import

import argparse
import logging
import json
import getpass

from .. import __version__, get_credentials, validate_filters, get_filter
from ..management.foreman import ForemanAPIClient

try:
    raw_input
except NameError:  # Python 3
    raw_input = input

"""
str: Program version
"""
LOGGER = logging.getLogger('katprep_parameters')
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
PARAMETERS = {
    "katprep_mon" : "URL of the monitoring system",
    "katprep_virt" : "Virtualization URL of the system",
    "katprep_virt_snapshot" : "Boolean whether system needs to be"\
    " protected by a snapshot before maintenance",
    "katprep_owner" : "System owner"
}
"""
dict: Built-in default host parameters mandatory for katprep
"""
OPT_PARAMETERS = {
    "katprep_mon_name" : "Object name within monitoring if not FQDN",
    "katprep_mon_type" : "Monitoring system type: nagios/(icinga)",
    "katprep_virt_name": "Object name within hypervisor if not FQDN",
    "katprep_virt_type": "Virtualization host type: (libvirt)/pyvmomi",
    "katprep_pre-script": "Script to run before maintenance",
    "katprep_post-script": "Script to run after maintenance"
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

    params = PARAMETERS.copy()
    params.update(OPT_PARAMETERS)
    for key, value in params.items():
        LOGGER.info(
            "Setting '%s' will define '%s'", key, value
        )



def change_param(options, host, mode="add", dry_run=True):
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
        if VALUES[param] != "":
            if dry_run:
                LOGGER.info(
                    "Host '%s' (#%s) --> %s parameter '%s'",
                    host["name"], host["id"], mode, param
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
                    "JSON payload: %s", str(json.dumps(payload))
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
        else:
            LOGGER.debug("Empty value for '%s', not changing anything!", param)



def manage_params(options):
    """
    Adds/removes/displays/updates parameter definitions.
    """

    #get all the hosts depending on the filter
    filter_url = get_filter(options, "host")
    LOGGER.debug("Filter URL will be '%s'", filter_url)
    result_obj = json.loads(
        SAT_CLIENT.api_get("{}".format(filter_url))
    )

    #manage _all_ the hosts
    for entry in result_obj["results"]:
        LOGGER.debug(
            "Found host '%s' (#%s),", entry["name"], entry["id"]
        )
        #execute action
        if options.action_add or options.action_addopt:
            change_param(options, entry, "add", options.dry_run)
        elif options.action_update:
            change_param(options, entry, "update", options.dry_run)
        elif options.action_remove:
            change_param(options, entry, "del", options.dry_run)
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
                        "Host '%s' (#%s) --> setting '%s' has %s value '%s'"
                        " (created: %s - last updated: %s)",
                        entry["name"], entry["id"], setting["name"],
                        note, setting["value"], setting["created_at"],
                        setting["updated_at"]
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
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument('--version', action='version', version=__version__)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    srv_opts = parser.add_argument_group("server arguments")
    filter_opts = parser.add_argument_group("filter arguments")
    filter_opts_excl = filter_opts.add_mutually_exclusive_group()
    action_opts = parser.add_argument_group("action arguments")
    action_opts_excl = action_opts.add_mutually_exclusive_group(required=True)

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", \
    dest="generic_quiet", default=False, help="don't print status messages " \
    "to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="generic_debug", default=False, \
    action="store_true", help="enable debugging outputs (default: no)")
    #-n / --dry-run
    gen_opts.add_argument("-n", "--dry-run", dest="dry_run", default=False, \
    action="store_true", help="only simulate what would be done (default: no)")
    #-C / --auth-container
    gen_opts.add_argument("-C", "--auth-container", default="", \
    dest="auth_container", action="store", metavar="FILE", \
    help="defines an authentication container file (default: no)")
    #-P / --auth-password
    gen_opts.add_argument("-P", "--auth-password", default="empty", \
    dest="auth_password", action="store", metavar="PASSWORD", \
    help="defines the authentication container password in case you don't " \
    "want to enter it manually (useful for scripted automation)")

    #SERVER ARGUMENTS
    #-s / --server
    srv_opts.add_argument("-s", "--server", dest="server", metavar="SERVER", \
    default="localhost", help="defines the server to use (default: localhost)")
    #--insecure
    srv_opts.add_argument("--insecure", dest="ssl_verify", default=True, \
    action="store_false", help="Disables SSL verification (default: no)")

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
    help="lists values of defined parameters for affected hosts (default: no)")
    #-U / --update-parameters
    action_opts_excl.add_argument("-U", "--update-parameters", \
    action="store_true", default=False, dest="action_update", \
    help="updates values of defined parameters for affected hosts (default: no)")
    #-L / --list-parameters
    action_opts_excl.add_argument("-L", "--list-parameters", \
    action="store_true", default=False, dest="action_list", \
    help="only lists parameters this script uses (default: no)")



    #parse options and arguments
    options = parser.parse_args()
    while options.auth_password == "empty" or len(options.auth_password) > 32:
        options.auth_password = getpass.getpass(
            "Authentication container password: "
        )
    return (options, args)



def main(options, args):
    """Main function, starts the logic based on parameters."""
    global SAT_CLIENT

    LOGGER.debug("Options: %s", str(options))
    LOGGER.debug("Arguments: %s", str(args))

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
            #while user_input == "":
            user_input = raw_input(
                "Enter value for '{}' (hint: {}): ".format(
                    param, PARAMETERS[param]
                )
            )
            VALUES[param] = user_input

    if not options.action_list:
        #initalize Satellite connection
        (sat_user, sat_pass) = get_credentials(
            "Satellite", options.server, options.auth_container,
            options.auth_password
        )
        SAT_CLIENT = ForemanAPIClient(
            LOG_LEVEL, options.server, sat_user,
            sat_pass, options.ssl_verify
        )

        #validate filters
        validate_filters(options, SAT_CLIENT)

        #do the stuff
        manage_params(options)


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
