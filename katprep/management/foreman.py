#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file contains the ForemanAPIClient class
"""

import logging
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .exceptions import (APILevelNotSupportedException,
InvalidCredentialsException, InvalidHostnameFormatException
SessionException)


class ForemanAPIClient:
    """
    Class for communicating with the Foreman API

.. class:: ForemanAPIClient
    """
    LOGGER = logging.getLogger('ForemanAPIClient')
    """
    logging: Logger instance
    """
    API_MIN = 2
    """
    int: Minimum supported API version. You really don't want to use v1.
    """
    HEADERS = {'User-Agent': 'katprep (https://github.com/stdevel/katprep)'}
    """
    dict: Default headers set for every HTTP request
    """
    HOSTNAME = ""
    """
    str: Foreman API hostname
    """
    URL = ""
    """
    str: Foreman API base URL
    """
    SESSION = None
    """
    Session: HTTP session to Foreman host
    """
    VERIFY = True
    """
    bool: Boolean whether force SSL verification
    """

    def __init__(self, log_level, hostname,
                 username, password, verify=True, prefix=""):
        """
        Constructor, creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param hostname: Foreman host
        :type hostname: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param verify: force SSL verification
        :type verify: bool
        :param prefix: API prefix (e.g. /katello)
        :type prefix: str
        """
        #set logging
        self.LOGGER.setLevel(log_level)
        #disable SSL warning outputs
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        #set connection information
        self.HOSTNAME = hostname
        self.USERNAME = username
        self.PASSWORD = password
        self.VERIFY = verify
        self.URL = "https://{0}{1}/api/v2".format(self.HOSTNAME, prefix)
        #start session and check API version if Foreman API
        self.__connect()
        if prefix == "":
            self.validate_api_support()



    def __connect(self):
        """
        This function establishes a connection to Foreman.
        """
        global SESSION
        self.SESSION = requests.Session()
        self.SESSION.auth = (self.USERNAME, self.PASSWORD)



    def get_hostname(self):
        """
        Returns the configured hostname of the object instance.
        """
        return self.HOSTNAME



    #TODO: find a nicer way to displaying _all_ the hits...
    def __api_request(self, method, sub_url, payload="", hits=1337, page=1):
        """
        Sends a HTTP request to the Foreman API. This function requires
        a valid HTTP method and a sub-URL (such as /hosts). Optionally,
        you can also specify payload (for POST, DELETE, PUT) and hits/page
        and a page number (when retrieving data using GET).
        There are also alias functions available.

        :param method: HTTP request method (GET, POST, DELETE, PUT)
        :type method: str
        :param sub_url: relative path within the API tree (e.g. /hosts)
        :type sub_url: str
        :param payload: payload for POST/PUT requests
        :type payload: str
        :param hits: numbers of hits/page for GET requests (must be set sadly)
        :type hits: int
        :param page: number of page/results to display (must be set sadly)
        :type page: int

.. todo:: Find a nicer way to display all hits, we shouldn't use 1337 hits/page

.. seealso:: api_get()
.. seealso:: api_post()
.. seealso:: api_put()
.. seealso:: api_delete()
        """
        #send request to API
        try:
            if method.lower() not in ["get", "post", "delete", "put"]:
                #going home
                raise SessionException("Illegal method '{}' specified".format(method))

            self.LOGGER.debug(
                "%s request to %s%s (payload: %s)", method.upper(), self.URL,
                sub_url, str(payload)
            )
            #setting headers
            my_headers = self.HEADERS
            if method.lower() != "get":
                #add special headers for non-GETs
                my_headers["Content-Type"] = "application/json"
                my_headers["Accept"] = "application/json,version=2"

            #send request
            if method.lower() == "put":
                #PUT
                result = self.SESSION.put(
                    "{}{}".format(self.URL, sub_url),
                    data=payload, headers=my_headers, verify=self.VERIFY
                )
            elif method.lower() == "delete":
                #DELETE
                result = self.SESSION.delete(
                    "{}{}".format(self.URL, sub_url),
                    data=payload, headers=my_headers, verify=self.VERIFY
                )
            elif method.lower() == "post":
                #POST
                result = self.SESSION.post(
                    "{}{}".format(self.URL, sub_url),
                    data=payload, headers=my_headers, verify=self.VERIFY
                )
            else:
                #GET
                result = self.SESSION.get(
                    "{}{}?per_page={}&page={}".format(
                        self.URL, sub_url, hits, page),
                    headers=self.HEADERS, verify=self.VERIFY
                )
            if "unable to authenticate" in result.text.lower():
                raise InvalidCredentialsException("Unable to authenticate")
            if result.status_code not in [200, 201, 202]:
                raise SessionException("{}: HTTP operation not successful {}".format(
                    result.status_code, result.text))
            else:
                #return result
                if method.lower() == "get":
                    return result.text
                else:
                    return True

        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)
            pass

    #Aliases
    def api_get(self, sub_url, hits=1337, page=1):
        """
        Sends a GET request to the Foreman API. This function requires a
        sub-URL (such as /hosts) and - optionally - hits/page and page
        definitons.

        :param sub_url: relative path within the API tree (e.g. /hosts)
        :type sub_url: str
        :param hits: numbers of hits/page for GET requests (must be set sadly)
        :type hits: int
        :param page: number of page/results to display (must be set sadly)
        :type page: int
        """
        return self.__api_request("get", sub_url, "", hits, page)

    def api_post(self, sub_url, payload):
        """
        Sends a POST request to the Foreman API. This function requires a
        sub-URL (such as /hosts/1) and payload data.

        :param sub_url: relative path within the API tree (e.g. /hosts)
        :type sub_url: str
        :param payload: payload for POST/PUT requests
        :type payload: str
        """
        return self.__api_request("post", sub_url, payload)

    def api_delete(self, sub_url, payload):
        """
        Sends a DELETE request to the Foreman API. This function requires a
        sub-URL (such as /hosts/2) and payload data.

        :param sub_url: relative path within the API tree (e.g. /hosts)
        :type sub_url: str
        :param payload: payload for POST/PUT requests
        :type payload: str
        """
        return self.__api_request("delete", sub_url, payload)

    def api_put(self, sub_url, payload):
        """
        Sends a PUT request to the Foreman API. This function requires a
        sub-URL (such as /hosts/3) and payload data.

        :param sub_url: relative path within the API tree (e.g. /hosts)
        :type sub_url: str
        :param payload: payload for POST/PUT requests
        :type payload: str
        """
        return self.__api_request("put", sub_url, payload)



    def validate_api_support(self):
        """
        Checks whether the API version on the Foreman server is supported.
        Using older version than API v2 is not recommended. In this case, an
        exception will be thrown.
        """
        try:
            #get api version
            result_obj = json.loads(
                self.api_get("/status")
            )
            self.LOGGER.debug("API version %s found", result_obj["api_version"])
            if result_obj["api_version"] != self.API_MIN:
                raise APILevelNotSupportedException(
                    "Your API version (%s) does not support the required calls."
                    "You'll need API version %s - stop using historic"
                    " software!", result_obj["api_version"], self.API_MIN
                )
        except ValueError as err:
            self.LOGGER.error(err)
            raise APILevelNotSupportedException("Unable to verify API version")



    def get_url(self):
        """Returns the configured URL of the object instance"""
        return self.URL



    def get_name_by_id(self, object_id, api_object):
        """
        Returns a Foreman object's name by its ID.

        param object_id: Foreman object ID
        type object_id: int
        param api_object: Foreman object type (e.g. host, environment)
        type api_object: str
        """
        valid_objects = [
            "hostgroup", "location", "organization", "environment",
            "host", "user"
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
                result_obj = json.loads(
                    self.api_get("/{}s/{}".format(api_object, object_id))
                )
                if result_obj["id"] == object_id:
                    self.LOGGER.debug(
                        "I think I found %s #%s...", api_object, object_id
                    )
                if api_object.lower() == "user":
                    return "{} {}".format(
                        result_obj["firstname"], result_obj["lastname"]
                    )
                else:
                    return result_obj["name"]
        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)



    def get_id_by_name(self, name, api_object):
        """
        Returns a Foreman object's internal ID by its name.

        :param name: Foreman object name
        :type name: str
        :param api_object: Foreman object type (e.g. host, environment)
        :type api_object: str
        """
        valid_objects = [
            "hostgroup", "location", "organization", "environment",
            "host"
        ]
        filter_object = {
            "hostgroup" : "title", "location": "name", "host" : "name",
            "organization" : "title", "environment" : "name"
        }
        try:
            if api_object.lower() not in valid_objects:
                #invalid type
                raise ValueError(
                    "Unable to lookup name by invalid field"
                    " type '{}'".format(api_object)
                )
            else:
                #get ID by name
                result_obj = json.loads(
                    self.api_get("/{}s".format(api_object))
                )
                #TODO: nicer way than looping? numpy? Direct URL?
                for entry in result_obj["results"]:
                    if entry[filter_object[api_object]].lower() == name.lower():
                        self.LOGGER.debug(
                            "%s %s seems to have ID #%s",
                            api_object, name, entry["id"]
                        )
                        return entry["id"]
                #not found
                raise SessionException("Object not found")
        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)



    def get_hostparam_id_by_name(self, host, param_name):
        """
        Returns a Foreman host parameter's internal ID by its name.

        :param host: Foreman host object ID
        :type host: int
        :param param_name: host parameter name
        :type param_name: str
        """
        #TODO: Move to get_id_by_name
        try:
            result_obj = json.loads(
                self.api_get("/hosts/{}/parameters".format(host))
            )
            #TODO: nicer way than looping? numpy?
            #TODO allow/return multiple IDs to reduce overhead?
            for entry in result_obj["results"]:
                if entry["name"].lower() == param_name.lower():
                    self.LOGGER.debug(
                        "Found relevant parameter '%s' with ID #%s",
                        entry["name"], entry["id"]
                    )
                    return entry["id"]

        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)



    def get_host_params(self, host):
        """
        Returns all parameters for a particular host.

        :param host: Forenam host name
        :type host: str
        """
        try:
            result_obj = json.loads(
                self.api_get("/hosts/{}/parameters".format(host))
            )
            return result_obj["results"]
        except ValueError as err:
            self.LOGGER.error(err)
            raise SessionException(err)



    def get_task_by_filter(self, host, task_name, task_date):
        """
        Returns host management tasks by filter

        :param host: Foreman host name
        :type host: str
        :param task_name: Filter argument
        :type task_name: str
        :param task_date: Task date wildcard
        :type task_date: str
        """
        try:
            my_results = []
            #get _all_ the results
            results = json.loads(
                self.api_get(
                    '/../../foreman_tasks/api/tasks?search="{}"' \
                    '&order="started_at DESC"'.format(task_name)
                )
            )
            #print results
            for result in results["results"]:
                #validate date and host
                host_info = result["input"]["host"]
                if host_info["name"] == host and \
                    task_date in result["started_at"]:
                    my_results.append(result)
        except KeyError:
            pass
        except ValueError as err:
            self.LOGGER.error(err)
        finally:
            return my_results
