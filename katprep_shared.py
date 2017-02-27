#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
katprep_shared.py - a shared library containing
functions and calls used by other scripts of the
katprep toolkit.

2017 By Christian Stankowic
<info at stankowic hyphen development dot net>
https://github.com/stdevel/katprep
"""

import getpass
import logging
import requests
import os
import stat
import simplejson
import argparse
import socket

LOGGER = logging.getLogger('katprep_shared')



class APILevelNotSupportedException(Exception):
    """Dummy class for unsupported API levels"""
    pass



def get_credentials(prefix, input_file=None):
    """Retrieves credentials for a particular external system (e.g. Satellite).

    Keyword arguments:
    prefix -- prefix for the external system (used in variables and prompts)
    input_file -- name of auth file (default none)
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
    elif prefix.upper()+"_LOGIN" in os.environ and prefix.upper()+"_PASSWORD" in os.environ:
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



#TODO: def has_snapshot(virt_uri, host_username, host_password, vm_name, name):
#check whether VM has a snapshot



#TODO: def is_downtime(url, mon_user, mon_pass, host, agent, no_auth=False):
#checker whether host is scheduled for downtime



#TODO: def schedule_downtime(url, mon_user, mon_pass, host, hours, comment, \
#no_auth=False, unschedule=False):
#(un)schedule downtime



#TODO: def schedule_downtime_hostgroup(url, mon_username, mon_password,}
# hostgroup, hours, comment, agent="", no_auth=False):
#schedule downtime for hostgroup



#TODO: def get_libvirt_credentials(credentials, user_data):
#get credentials for libvirt



#TODO: def create_snapshot(virt_uri, host_username, host_password, vm_name,\
#name, comment, remove=False):
#create/remove snapshot



def is_writable(path):
    """Checks whether a particular directory is writable.

    Keyword arguments:
    path -- path to check for write access
    """
    if os.access(os.path.dirname(path), os.W_OK):
        return True
    else:
        return False



def is_exe(file_path):
    """Returns whether a file is an executable

    Keyword arguments:
    file_path -- path to the file
    """
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)



def which(command):
    """Checks whether a command name links to an existing binary (like whoami).

    Keyword arguments:
    command -- command name to check
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
    """Reads a JSON file and returns the whole content as one-liner.

    Keyword arguments:
    filename -- the JSON filename
    """
    try:
        with open(filename, "r") as json_file:
            json_data = json_file.read().replace("\n", "")
        return json_data
    except IOError as err:
        LOGGER.error("Unable to read file '{}': '{}'".format(filename, err))



def is_valid_report(filename):
    """Checks whether a JSON file contains a valid snapshot report.

    Keyword arguments:
    filename -- the JSON filename
    """
    if not os.path.exists(filename) or not os.access(filename, os.R_OK):
        raise argparse.ArgumentTypeError("File '{}' non-existent or not" \
            " readable".format(filename))
    #check whether valid json
    try:
        json_obj = simplejson.loads(get_json(filename))
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



def validate_filters(options, api_client):
    """Ensures using IDs for the Foreman API rather than human-readable names.
    This is done by detecting strings and translating them into IDs.

    Keyword arguments:
    options -- argparse option object
    api_client -- ForemanAPIClient object
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
    """Sets up a filter URL based on arguments set-up with argpase.

    Keyword arguments:
    options -- argparse option object
    api_object -- Foreman object type (e.g. host, environment)
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






class ForemanAPIClient:
    """Class for accessing the Foreman API."""
    API_MIN = 2
    HEADERS = {'User-Agent': 'katprep Toolkit (https://github.com/stdevel/katprep)'}

    def __init__(self, hostname, username, password):
        """Constructor, creating the class."""
        self.hostname = self.validate_hostname(hostname)
        self.username = username
        self.password = password
        self.url = "https://{0}/api/v2".format(self.hostname)
        #check API version
        self.validate_api_support()

    #TODO: find a nicer way to displaying _all_ the hits...
    def api_request(self, method, sub_url, payload="", hits=1337, page=1):
        """Sends a HTTP request to the Foreman API.

        Keyword arguments:
        method -- HTTP request method (GET, POST, DELETE, PUT)
        sub_url -- relative path within the API tree (e.g. /hosts)
        payload -- payload for POST/PUT requests
        hits -- numbers of hits/page for GET requests (sadly it must be set)
        page -- number of page/results to display (sadly this must be set, too)
        """
        #send request to API
        try:
            if method.lower() not in ["get", "post", "delete", "put"]:
                #going home
                raise ValueError("Illegal method '{}' specified".format(method))

            #setting headers
            my_headers = self.HEADERS
            if method.lower() != "get":
                #add special headers for non-GETs
                my_headers["Content-Type"] = "application/json"
                my_headers["Accept"] = "application/json,version=2"

            #send request
            if method.lower() == "put":
                #PUT
                result = requests.put("{}{}".format(self.url, sub_url),
                                      data=payload, headers=my_headers,
                                      auth=(self.username, self.password)
                                     )
            elif method.lower() == "delete":
                #DELETE
                result = requests.delete("{}{}".format(self.url, sub_url),
                                         data=payload, headers=my_headers,
                                         auth=(self.username, self.password)
                                        )
            elif method.lower() == "post":
                #POST
                result = requests.post("{}{}".format(self.url, sub_url),
                                       data=payload, headers=my_headers,
                                       auth=(self.username, self.password)
                                      )
            else:
                #GET
                result = requests.get(
                    "{}{}?per_page={}&page={}".format(
                        self.url, sub_url, hits, page),
                    headers=self.HEADERS, auth=(self.username, self.password)
                )
            if "unable to authenticate" in result.text.lower():
                raise ValueError("Unable to authenticate")
            if result.status_code not in [200, 201, 202]:
                raise ValueError("{}: HTTP operation not successful".format(
                    result.status_code))
            else:
                #return result
                if method.lower() == "get":
                    return result.text
                else:
                    return True

        except ValueError as err:
            LOGGER.error(err)
            raise

    #Aliases
    def api_get(self, sub_url, hits=1337, page=1):
        """Sends a GET request to the Foreman API.

        Keyword arguments:
        sub_url -- relative path within the API tree (e.g. /hosts)
        hits -- numbers of hits/page for GET requests (sadly it must be set)
        page -- number of page/results to display (sadly this must be set, too)
        """
        return self.api_request("get", sub_url, "", hits, page)

    def api_post(self, sub_url, payload):
        """Sends a POST request to the Foreman API.

        Keyword arguments:
        sub_url -- relative path within the API tree (e.g. /hosts)
        payload -- payload for POST/PUT requests
        """
        return self.api_request("post", sub_url, payload)

    def api_delete(self, sub_url, payload):
        """Sends a DELETE request to the Foreman API.

        Keyword arguments:
        sub_url -- relative path within the API tree (e.g. /hosts)
        payload -- payload for POST/PUT requests
        """
        return self.api_request("delete", sub_url, payload)

    def api_put(self, sub_url, payload):
        """Sends a PUT request to the Foreman API.

        Keyword arguments:
        sub_url -- relative path within the API tree (e.g. /hosts)
        payload -- payload for POST/PUT requests
        """
        return self.api_request("put", sub_url, payload)



    def validate_api_support(self):
        """Checks whether the API version on the Foreman server is supported"""
        try:
            #get api version
            result_obj = simplejson.loads(
                self.api_get("/status")
            )
            LOGGER.debug("API version {} found.".format(
                result_obj["api_version"]))
            if result_obj["api_version"] != self.API_MIN:
                raise APILevelNotSupportedException(
                    "Your API version ({}) does not support the required calls."
                    "You'll need API version {} - stop using historic"
                    " software!".format(result_obj["api_version"], self.API_MIN)
                )
        except ValueError as err:
            LOGGER.error(err)



    def validate_hostname(self, hostname):
        """Validates that the Foreman API uses a FQDN as hostname.
        Also looks up localhost definitions and uses the "real" hostname.
        Otherwise, the picky Foreman API won't connect.

        Keyword arguments:
        hostname -- the hostname to validate
        """
        if hostname == "localhost":
            #get real hostname
            hostname = socket.gethostname()
        else:
            #convert to FQDN if possible:
            fqdn = socket.gethostbyaddr(hostname)
            if "." in fqdn[0]:
                hostname = fqdn[0]
        return hostname



    def get_url(self):
        """Returns the configured URL of the object instance"""
        return self.url

    def get_id_by_name(self, name, api_object):
        """Returns a Foreman object's internal ID by its name.

        Keyword arguments:
        name -- Foreman object name
        api_object -- Foreman object type (e.g. host, environment)
        """
        valid_objects = [
            "hostgroup", "location", "organization", "environment", "host"
        ]
        try:
            if api_object.lower() not in valid_objects:
                #invalid type
                raise ValueError(
                    "Unable to lookup name by invalid field"
                    " type '{}'".format(api_object)
                )
            else:
                #get ID by name
                result_obj = simplejson.loads(
                    self.api_get("/{}s".format(api_object))
                )
                #TODO: nicer way than looping? numpy?
                for entry in result_obj["results"]:
                    if entry["name"].lower() == name.lower():
                        LOGGER.debug(
                            "{} {} seems to have ID #{}".format(
                                api_object, name, entry["id"]
                            )
                        )
                        return entry["id"]
        except ValueError as err:
            LOGGER.error(err)



    def get_hostparam_id_by_name(self, host, param_name):
        """Returns a Foreman host parameter's internal ID by its name.

        Keyword arguments:
        host -- Foreman host object ID
        param_name -- host parameter name
        """
        try:
            result_obj = simplejson.loads(
                self.api_get("/hosts/{}/parameters".format(host))
            )
            #TODO: nicer way than looping? numpy?
            #TODO allow/return multiple IDs to reduce overhead?
            for entry in result_obj["results"]:
                if entry["name"].lower() == param_name.lower():
                    LOGGER.debug(
                        "Found relevant parameter '{}' with ID #{}".format(
                            entry["name"], entry["id"]
                        )
                    )
                    return entry["id"]

        except ValueError as err:
            LOGGER.error(err)
