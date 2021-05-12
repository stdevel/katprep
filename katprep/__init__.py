#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A shared library containing functions used by other scripts of the
katprep toolkit.
"""

from __future__ import absolute_import, print_function

import getpass
import logging
import os
import json
import argparse
from .AuthContainer import AuthContainer, ContainerException
from .exceptions import SessionException

try:
    raw_input
except NameError:  # Python 3
    raw_input = input

__version__ = "0.5.0"

LOGGER = logging.getLogger('katprep_shared')
"""
logging: Logger instance
"""



def get_credentials(prefix, hostname=None, auth_container=None, auth_pass=None):
    """
    Retrieves credentials for a particular external system (e.g. Satellite).
    This function checks whether a hostname is part of an authentication
    container or retrieves credentials from an authentication file. If both
    approaches fail, logon credentials are prompted.

    :param prefix: prefix for the external system (used in variables/prompts)
    :type prefix: str
    :param hostname: external system hostname
    :type hostname: str
    :param auth_container: authentication container file name
    :type auth_container: str
    :param auth_pass: authentication container password
    :type auth_pass: str
    """
    if auth_container:
        LOGGER.debug("Using authentication container")
        try:
            container = AuthContainer(
                logging.ERROR, auth_container, auth_pass)
            s_creds = container.get_credential(hostname)
            if not s_creds:
                raise TypeError("Empty response")
            elif not 2 == len(s_creds):
                raise TypeError("Invalid response")

            return (s_creds.username, s_creds.password)
        except ContainerException as e:
            LOGGER.error(e)
            sys.exit(1)
        except TypeError:
            LOGGER.warning(
                "Login information for '{}' not found in container!".format(
                    hostname
                )
            )
            LOGGER.debug("Prompting for {} login credentials as we still" \
                " haven't found what we're looking for".format(prefix))
            s_username = raw_input(prefix + " Username: ")
            s_password = getpass.getpass(prefix + " Password: ")
            return (s_username, s_password)
    elif prefix.upper()+"_LOGIN" in os.environ and \
        prefix.upper()+"_PASSWORD" in os.environ:
        #shell variables
        LOGGER.debug("Checking {} shell variables".format(prefix))
        return (os.environ[prefix.upper()+"_LOGIN"], \
            os.environ[prefix.upper()+"_PASSWORD"])
    else:
        #prompt user
        LOGGER.debug("Prompting for {} login credentials".format(prefix))
        s_username = raw_input(prefix + " Username: ")
        s_password = getpass.getpass(prefix + " Password: ")
        return (s_username, s_password)



def is_writable(path):
    """
    Checks whether a particular directory is writable.

    :param path: path to check for write access
    :type path: str
    """
    if os.access(os.path.dirname(path), os.W_OK):
        return True
    else:
        return False



def is_exe(file_path):
    """
    Returns whether a file is an executable

    :param file_path: path to the file
    :type file_path: str
    """
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)



def which(command):
    """
    Checks whether a command name links to an existing binary (like whoami).

    :param command: command name to check
    :type command: str
    """
    #stackoverflow.com/questions/377017/test-if-executable-exists-in-python

    fpath, fname = os.path.split(command)
    if fpath:
        if is_exe(command):
            return command
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, command)
            if is_exe(exe_file):
                return exe_file
    return None


def validate_filters(options, api_client):
    """
    Ensures using IDs for the Foreman API rather than human-readable names.
    This is done by detecting strings and translating them into IDs.

    :param options: argparse options dict
    :type options: dict
    :param api_client: ForemanAPIClient object
    :type api_client: ForemanAPIClient
    """
    try:
        if options.location and options.location.isdigit() == False:
            options.location = api_client.get_id_by_name(
                options.location, "location")
        if options.organization and options.organization.isdigit() == False:
            options.organization = api_client.get_id_by_name(
                options.organization, "organization")
        if options.hostgroup and options.hostgroup.isdigit() == False:
            options.hostgroup = api_client.get_id_by_name(
                options.hostgroup, "hostgroup")
        if options.environment and options.environment.isdigit() == False:
            options.environment = api_client.get_id_by_name(
                options.environment, "environment")
    except SessionException:
        pass
    except Exception as err:
        print(err)


def get_filter(options, api_object):
    """
    Sets up a filter URL based on arguments set-up with argpase.

    :param options: argparse options dict
    :type options: dict
    :param api_object: Foreman object type (e.g. host, environment)
    :type api_object: str
    """
    if options.location:
        return "/locations/{}/{}s".format(options.location, api_object)
    elif options.organization:
        return "/organizations/{}/{}s".format(options.organization, api_object)
    elif options.hostgroup:
        return "/hostgroups/{}/{}s".format(options.hostgroup, api_object)
    elif options.environment:
        return "/environments/{}/{}s".format(options.environment, api_object)
    else:
        return "/{}s".format(api_object)
