#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script which maintains entries in a authentication container.
"""

from __future__ import absolute_import

import argparse
import logging
import json
import getpass
from .AuthContainer import AuthContainer

__version__ = "0.0.1"
LOGGER = logging.getLogger('katprep_authconfig')
"""
logging: Logger instance
"""
CONTAINER = None
"""
AuthContainer: authentication container file
"""



def list(options):
    """
    This function lists entries from the authentication container.
    """
    for hostname in CONTAINER.get_hostnames():
        #get credentials
        credentials = CONTAINER.get_credential(hostname)
        if options.show_passwords:
            password = credentials[1]
        else:
            password = "xxx"
        #print entry
        print "{} (Username: {} / Password: {})".format(
            hostname, credentials[0], password
        )



def add(options):
    """
    This function adds/modifies an entry to/from the authentication container.
    """
    while options.entry_hostname == "":
        #prompt for hostname
        options.entry_hostname = raw_input("Hostname: ")
    while options.entry_username == "":
        #prompt for hostname
        options.entry_username = raw_input(
            "{} Username: ".format(options.entry_hostname)
        )
    password_prompted=False
    while options.entry_password == "":
        #prompt for password
        password_prompted=True
        options.entry_password = getpass.getpass(
            "{} Password: ".format(options.entry_hostname)
        )
    #prompt again
    if not password_prompted:
        verification = options.entry_password
    else:
        verification = ""
    while verification != options.entry_password:
        verification = getpass.getpass(
            "Verify {} Password: ".format(options.entry_hostname)
        )
    LOGGER.debug("Adding entry hostname='{}', username='{}'...".format(
        options.entry_hostname, options.entry_username)
    )
    CONTAINER.add_credentials(
        options.entry_hostname, options.entry_username, options.entry_password
    )
    CONTAINER.save()



def remove(options):
    """
    This function removes an entry from the authentication container.
    """
    while options.entry_hostname == "":
        #prompt for hostname
        options.entry_hostname = raw_input("Hostname: ")
    LOGGER.debug("Removing entry hostname='{}'...".format(
        options.entry_hostname)
    )
    CONTAINER.remove_credentials(options.entry_hostname)
    CONTAINER.save()



def set_password(options):
    """
    This function sets/changes/removes the authentication container password.
    """
    #get password and build new container
    if options.file_password:
        new_pass = options.file_password
    else:
        new_pass = getpass.getpass("New file password (max. 32 chars): ")
    confirm=""
    while confirm != new_pass:
        confirm = getpass.getpass("Confirm password: ")
    new_container = AuthContainer(options.container[0], new_pass)

    #encrypt/change _all_ the passwords!
    for hostname in CONTAINER.get_hostnames():
        #get credentials
        credentials = CONTAINER.get_credential(hostname)
        #add new entry
        new_container.add_credentials(
            hostname, credentials[0], credentials[1]
        )
    #save new container
    new_container.save()



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for creating, modifying and
    removing entries in/from an authentication container.
    Authentication containers include various authentication credentials for
    external systems that can be accessed from the katprep utilities (e.g.
    monitoring systems, hypervisor connections, etc.).
    This will make system maintenance automation easier as you don't have to
    enter credentials every time.
    '''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(
        description=desc, version=__version__, epilog=epilog
    )

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", \
    dest="generic_quiet", \
    default=False, help="don't print status messages to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="generic_debug", \
    default=False, action="store_true", \
    help="enable debugging outputs (default: no)")
    #authentication container
    gen_opts.add_argument('container', metavar='FILE', nargs=1, \
    help='An authentication container', type=str)

    #COMMANDS
    subparsers = parser.add_subparsers(title='commands', \
    description='controlling maintenance stages', help='additional help')
    cmd_list = subparsers.add_parser("list", help="listing entries")
    cmd_list.add_argument("-a", "--show-passwords", action="store_true", \
    dest="show_passwords", default=False, help="also shows passwords " \
    "(default: no)")
    cmd_list.set_defaults(func=list)

    cmd_add = subparsers.add_parser("add", help="adding/modifying entries")
    cmd_add.add_argument("-H", "--hostname", action="store", default="", \
    dest="entry_hostname", metavar="HOSTNAME", help="hostname entry")
    cmd_add.add_argument("-u", "--username", action="store", default="", \
    dest="entry_username", metavar="USERNAME", help="username")
    cmd_add.add_argument("-p", "--password", action="store", default="", \
    dest="entry_password", metavar="PASSWORD", help="corresponding password")
    cmd_add.set_defaults(func=add)

    cmd_remove = subparsers.add_parser("remove", help="removing entries")
    cmd_remove.add_argument("-H", "--hostname", action="store", default="", \
    dest="entry_hostname", metavar="HOSTNAME", help="hostname entry")
    cmd_remove.set_defaults(func=remove)

    cmd_password = subparsers.add_parser("password", help="add/change/remove " \
    "encryption password")
    cmd_password.add_argument("-p", "--password", action="store", \
    dest="file_password", metavar="PASSWORD", help="password")
    cmd_password.set_defaults(func=set_password)

    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def main(options, args):
    """Main function, starts the logic based on parameters."""
    global CONTAINER

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    #prompt for password
    container_pass = "JaHaloIBimsDiPaulaPinkePank#Ohman"
    while len(container_pass) > 32:
        container_pass = getpass.getpass("File password (max. 32 chars): ")
    #load container
    CONTAINER = AuthContainer(options.container[0], container_pass)

    #start action
    options.func(options)


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
