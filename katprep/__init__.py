#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A shared library containing functions used by other scripts of the
katprep toolkit.
"""

from __future__ import absolute_import

import getpass
import logging
import os
import stat
import json
import argparse
from .AuthContainer import AuthContainer, ContainerException
from .clients import SessionException

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
            s_creds = None
            s_creds = container.get_credential(hostname)
            if len(s_creds) == 2:
                return (s_creds[0], s_creds[1])
            else:
                raise TypeError("Invalid response")
        except ContainerException as e:
            LOGGER.error(e)
            exit(1)
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
    except Exception as err:
        print err
    except SessionException:
        pass



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



def get_required_hosts_by_report(report, key):
    """
    Retrieves all required external hosts (such as monitoring systems
    or hypervisor connections) for maintaining hosts mentioned in a
    report.

    :param report: report dictionary
    :type report: dict
    :param key: key that contains hostname (e.g. katprep_virt)
    :type key: str
    """
    hosts=[]
    try:
        for host in report:
            if report[host]["params"][key] != "" and report[host]["params"][key] not in hosts:
                hosts.append(report[host]["params"][key])
    except KeyError:
            LOGGER.info("Key '{}' not found for host '{}'".format(key, host))
            pass
    return hosts



def get_host_params_by_report(report, host):
    """
    Retrieves all parameters for a particular host from a report.

    :param report: report dictionary
    :type report: dict
    :param host: hostname
    :type host: str
    """
    try:
        for entry in report:
            return report[entry]["params"]
    except KeyError:
            LOGGER.info("Parameters not found for host '{}'".format(host))
            pass
