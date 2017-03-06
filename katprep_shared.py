#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A shared library containing functions used by other scripts of the
katprep toolkit.
"""

import getpass
import logging
import os
import stat
import json
import argparse

LOGGER = logging.getLogger('katprep_shared')
"""
logging: Logger instance
"""



def get_credentials(prefix, input_file=None):
    """
    Retrieves credentials for a particular external system (e.g. Satellite).

    :param prefix: prefix for the external system (used in variables/prompts)
    :type prefix: str
    :param input_file: name of the auth file (default: none)
    :type input_file: str
    """
    if input_file:
        LOGGER.debug("Using authfile")
        try:
            #check filemode and read file
            filemode = oct(stat.S_IMODE(os.lstat(input_file).st_mode))
            if filemode == "0600":
                LOGGER.debug("File permission matches 0600")
                with open(input_file, "r") as auth_file:
                    s_username = auth_file.readline().replace("\n", "")
                    s_password = auth_file.readline().replace("\n", "")
                return (s_username, s_password)
            else:
                LOGGER.warning("File permissions (" + filemode + ")" \
                    " not matching 0600!")
        except OSError:
            LOGGER.warning("File non-existent or permissions not 0600!")
            LOGGER.debug("Prompting for {} login credentials as we have a" \
                " faulty file".format(prefix))
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



def get_json(filename):
    """
    Reads a JSON file and returns the whole content as one-liner.

    :param filename: the JSON filename
    :type filename: str
    """
    try:
        with open(filename, "r") as json_file:
            json_data = json_file.read().replace("\n", "")
        return json_data
    except IOError as err:
        LOGGER.error("Unable to read file '{}': '{}'".format(filename, err))



def is_valid_report(filename):
    """
    Checks whether a JSON file contains a valid snapshot report.

    :param filename: the JSON filename
    :type filename: str
    """
    if not os.path.exists(filename) or not os.access(filename, os.R_OK):
        raise argparse.ArgumentTypeError("File '{}' non-existent or not" \
            " readable".format(filename))
    #check whether valid json
    try:
        json_obj = json.loads(get_json(filename))
        #check whether at least one host with a params dict is found
        if "params" not in json_obj.itervalues().next().keys():
            raise argparse.ArgumentTypeError("File '{}' is not a valid JSON" \
                " snapshot report.".format(filename))
    except StopIteration as err:
        raise argparse.ArgumentTypeError("File '{}' is not a valid JSON" \
            " snapshot report.".format(filename))
    except ValueError as err:
        raise argparse.ArgumentTypeError("File '{}' is not a valid JSON" \
            " document: '{}'".format(filename, err))
    return filename



def validate_filters(options, api_client):
    """
    Ensures using IDs for the Foreman API rather than human-readable names.
    This is done by detecting strings and translating them into IDs.

    :param options: argparse options dict
    :type options: dict
    :param api_client: ForemanAPIClient object
    :type api_client: ForemanAPIClient
    """
    if options.location.isdigit() == False:
        options.location = api_client.get_id_by_name(
            options.location, "location")
    if options.organization.isdigit() == False:
        options.organization = api_client.get_id_by_name(
            options.organization, "organization")
    if options.hostgroup.isdigit() == False:
        options.hostgroup = api_client.get_id_by_name(
            options.hostgroup, "hostgroup")
    if options.environment.isdigit() == False:
        options.environment = api_client.get_id_by_name(
            options.environment, "environment")



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
