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
from ..exceptions import CustomVariableExistsException, EmptySetException
from ..management import get_management_client


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
    "katprep_pre-script_user": "Effective pre-script user",
    "katprep_pre-script_group": "Effective pre-script group",
    "katprep_post-script": "Script to run after maintenance",
    "katprep_post-script_user": "Effective post-script user",
    "katprep_post-script_group": "Effective post-script group"
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

    :param host: Host ID
    :type host: int
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

    if options.include_opt:
        # add optional parameters
        my_params = PARAMETERS
        my_params.update(OPT_PARAMETERS)
    else:
        # add mandatory parameters
        my_params = PARAMETERS

    hostname = SAT_CLIENT.get_hostname_by_id(host)
    LOGGER.debug(hostname)

    # alter parameters
    for param in my_params:
        try:
            if dry_run:
                LOGGER.info(
                    "Host '%s' (#%s) --> %s parameter '%s'",
                    hostname, host, mode, param
                )
                continue

            if mode.lower() == "add":
                # create parameters
                LOGGER.debug(
                    "Creating param '%s' ('%s')",
                    param, my_params[param]
                )
                SAT_CLIENT.create_custom_variable(param, my_params[param])

            elif mode.lower() == "update":
                # update parameter
                LOGGER.debug(
                    "Updating param '%s' ('%s') for %s",
                    param, VALUES[param], hostname
                )
                SAT_CLIENT.host_update_custom_variable(host, param, VALUES[param])

            elif mode.lower() == "delete":
                # delete parameter
                LOGGER.debug(
                    "Removing param '%s' ('%s') from %s",
                    param, my_params[param], hostname
                )
                SAT_CLIENT.host_delete_custom_variable(host, param)

        except EmptySetException:
            # don't add empty value
            pass
        except CustomVariableExistsException:
            pass



def manage_params(options):
    """
    Adds/removes/displays/updates parameter definitions.
    """
    # get all the hosts depending on the filter
    if options.location:
        hosts = SAT_CLIENT.get_hosts_by_location(options.location)
    elif options.organization:
        hosts = SAT_CLIENT.get_hosts_by_organization(options.organization)
    elif options.hostgroup:
        hosts = SAT_CLIENT.get_hosts_by_hostgroup(options.hostgroup)
    else:
        hosts = SAT_CLIENT.get_hosts()
    LOGGER.debug("Hosts found: %s", hosts)

    # manage hosts/parameters
    for host in hosts:
        if options.action_add:
            change_param(options, host, "add", options.dry_run)
        elif options.action_update:
            change_param(options, host, "update", options.dry_run)
        elif options.action_remove:
            change_param(options, host, "delete", options.dry_run)
        else:
            # print current host parameters
            LOGGER.debug("Displaying parameter values...")
            hostname = SAT_CLIENT.get_hostname_by_id(host)

            params = SAT_CLIENT.get_host_custom_variables(host)
            for _param in params:
                LOGGER.info(
                    "Host '%s' (#%s) --> setting '%s' has value '%s'",
                    hostname,
                    host,
                    _param,
                    params[_param],
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
    #--include-optional-parameters
    gen_opts.add_argument("--include-optional-parameters", \
    action="store_true", default=False, dest="include_opt", \
    help="includes optional built-in parameters to all affected hosts (default: no)")

    #SERVER ARGUMENTS
    #--mgmt-type
    srv_opts.add_argument(
        "--mgmt-type",
        dest="mgmt_type",
        metavar="foreman|uyuni",
        choices=["foreman", "uyuni"],
        default="foreman",
        type=str,
        help="defines the library used to operate with management host: "
        "foreman or uyuni (default: foreman)",
    )
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

    #ACTION ARGUMENTS
    #-A / --add-parameters
    action_opts_excl.add_argument("-A", "--add-parameters", \
    action="store_true", default=False, dest="action_add", \
    help="adds built-in parameters to all affected hosts (default: no)")
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

    params = PARAMETERS.copy()
    if options.include_opt:
        params.update(OPT_PARAMETERS)

    if options.action_update:
        # retrieve values for parameters
        for param in params:
            #prompt for _all_ the parameters
            user_input = input(
                "Enter value for '{}' (hint: {}): ".format(
                    param, params[param]
                )
            )
            VALUES[param] = user_input

    if not options.action_list:
        #initalize Satellite connection
        (management_user, management_password) = get_credentials(
            f"Management ({options.mgmt_type})", options.server, options.auth_container,
            options.auth_password
        )
        SAT_CLIENT = get_management_client(
            options.mgmt_type, LOG_LEVEL,
            management_user, management_password, options.server,
            verify=options.ssl_verify
        )

        #validate filters
        # TODO: validate_filters(options, SAT_CLIENT)

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
