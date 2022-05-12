#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
A script for creating a snapshot report of available errata and updates for
systems managed with Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import

import argparse
import logging
import json
import time
import getpass
from .. import (__version__, get_credentials, is_writable)
from ..exceptions import SessionException
from ..management import get_management_client
from ..network import validate_hostname

LOGGER = logging.getLogger("katprep_snapshot")
"""
logging: Logger instance
"""
LOG_LEVEL = None
"""
logging: Logger level
"""
MGMT_CLIENT = None
"""
MGMT_CLIENT: Management client
"""
OUTPUT_FILE = ""
"""
str: Output file
"""


def parse_options(args=None):
    """Parses options and arguments."""

    desc = """%(prog)s is used for creating snapshot reports of
    errata available to your systems managed with Foreman/Katello or Red
    Hat Satellite 6. You can use two snapshot reports to create delta
    reports using katprep_report.
    Login credentials need to be entered interactively or specified using
    environment variables (SATELLITE_LOGIN, SATELLITE_PASSWORD) or an auth
    container.
    When using an auth container, ensure that the file permissions are 0600 -
    otherwise the script will abort. Maintain the auth container credentials
    with the katprep_authconfig utility.
    """
    epilog = """Check-out the website for more details:
http://github.com/stdevel/katprep"""
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument("--version", action="version", version=__version__)

    # define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    mgmt_opts = parser.add_argument_group("management arguments")
    filter_opts = parser.add_argument_group("filter arguments")
    filter_opts_excl = filter_opts.add_mutually_exclusive_group()

    # GENERIC ARGUMENTS
    # -q / --quiet
    gen_opts.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="generic_quiet",
        default=False,
        help="don't print status messages to stdout (default: no)",
    )
    # -d / --debug
    gen_opts.add_argument(
        "-d",
        "--debug",
        dest="generic_debug",
        default=False,
        action="store_true",
        help="enable debugging outputs (default: no)",
    )
    # -p / --output-path
    gen_opts.add_argument(
        "-p",
        "--output-path",
        dest="output_path",
        metavar="PATH",
        default="",
        action="store",
        help="The directory where reports are stored "
        "(default: current directory)",
    )
    # -C / --auth-container
    gen_opts.add_argument(
        "-C",
        "--auth-container",
        dest="auth_container",
        action="store",
        metavar="FILE",
        help="Which authentication container to use",
    )
    # -P / --auth-password
    gen_opts.add_argument(
        "-P",
        "--auth-password",
        default="empty",
        dest="auth_password",
        action="store",
        metavar="PASSWORD",
        help="Set the authentication container password. Useful for scripted automation.",
    )

    # MANAGEMENT ARGUMENTS
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
    # --insecure
    mgmt_opts.add_argument(
        "--insecure",
        dest="ssl_verify",
        default=True,
        action="store_false",
        help="Disables SSL verification (default: no)",
    )

    # SNAPSHOT FILTER ARGUMENTS
    # -l / --location
    filter_opts_excl.add_argument(
        "-l",
        "--location",
        action="store",
        default="",
        dest="location",
        metavar="NAME|ID",
        help="filters by a" " particular location (default: no)",
    )
    # -o / --organization
    filter_opts_excl.add_argument(
        "-o",
        "--organization",
        action="store",
        default="",
        dest="organization",
        metavar="NAME|ID",
        help="filters by an" " particular organization (default: no)",
    )
    # -g / --hostgroup
    filter_opts_excl.add_argument(
        "-g",
        "--hostgroup",
        action="store",
        default="",
        dest="hostgroup",
        metavar="NAME|ID",
        help="filters by a" " particular hostgroup (default: no)",
    )
    # -e / --environment
    filter_opts_excl.add_argument(
        "-e",
        "--environment",
        action="store",
        default="",
        dest="environment",
        metavar="NAME|ID",
        help="filters by an" " particular environment (default: no)",
    )
    # -E / --exclude
    filter_opts.add_argument(
        "-E",
        "--exclude",
        action="append",
        default=[],
        type=str,
        dest="filter_exclude",
        metavar="NAME",
        help="excludes particular hosts (default: no)",
    )

    # parse options and arguments
    options = parser.parse_args()
    # validate hostname
    options.server = validate_hostname(options.server)
    # set password
    while options.auth_password == "empty" or len(options.auth_password) > 32:
        options.auth_password = getpass.getpass(
            "Authentication container password: "
        )
    return (options, args)


def scan_systems(options):
    """
    Scans all systems that were selected for errata counters
    """
    system_info = {}

    # get information per system
    for system in MGMT_CLIENT.get_hosts():

        # TODO: exclude if blacklisted or filtered

        # get system information
        details = MGMT_CLIENT.get_host_details(system)
        network = MGMT_CLIENT.get_host_network(system)
        organization = MGMT_CLIENT.get_organization()
        location = MGMT_CLIENT.get_location()
        try:
            owner = MGMT_CLIENT.get_host_owner(system)
        except SessionException as sexc:
            LOGGER.debug("Skipping %s: %s", system, sexc)
            continue  # skip this client
        patches = MGMT_CLIENT.get_host_patches(system)
        upgrades = MGMT_CLIENT.get_host_upgrades(system)
        params = MGMT_CLIENT.get_host_params(system)

        host_id = details["id"]
        collected_information = {
            "id": host_id,
            "name": details["profile_name"],
            "hostname": details["hostname"],
            "description": details["description"],
            "virtualization": details["virtualization"],
            "organization": organization,
            "location": location,
            "params": params,
            "errata": patches,
            "upgrades": upgrades,
            "ip": network["ip"],
            "ipv6": network["ip6"],
            "owner": owner,
            "reboot_suggested": "TODO",     # TODO: find out how to get this data
        }

        system_info[host_id] = collected_information

    return system_info


def create_report(system_info):
    """
    Creates a JSON report including errata information of all hosts
    """
    if system_info:
        try:
            with open(OUTPUT_FILE, "w") as target:
                target.write(json.dumps(system_info))
        except IOError as err:
            LOGGER.error("Unable to store report: '%s'", err)
        else:
            LOGGER.info("Report '%s' created.", OUTPUT_FILE)
    else:
        LOGGER.info("Empty report - please check.")


def main(options, args):
    """
    Main function, starts the logic based on parameters
    """
    global MGMT_CLIENT, OUTPUT_FILE

    LOGGER.debug("Options: %s", options)
    LOGGER.debug("Arguments: %s", args)

    # set output file
    if options.output_path == "":
        options.output_path = "./"
    elif not options.output_path.endswith("/"):
        # add trailing slash
        options.output_path = "{}/".format(options.output_path)
    OUTPUT_FILE = "{}errata-snapshot-report-{}-{}.json".format(
        options.output_path,
        options.server.split(".")[0],
        time.strftime("%Y%m%d-%H%M")
    )
    LOGGER.debug("Output file will be: '%s'", OUTPUT_FILE)

    # check if we can read and write before digging
    if is_writable(OUTPUT_FILE):
        # initalize Foreman connection and scan systems
        (mgmt_user, mgmt_pass) = get_credentials(
            f"Management ({options.mgmt_type})",
            options.server,
            options.auth_container,
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

        # scan systems and create report
        info = scan_systems(options)
        create_report(info)
    else:
        LOGGER.error("Directory '%s' is not writable!", OUTPUT_FILE)


def cli():
    """
    This functions initializes the CLI interface
    """
    global LOG_LEVEL
    (options, args) = parse_options()

    # set logging level
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
