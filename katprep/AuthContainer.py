#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class for managing multiple authentication credentials
"""

import os
import stat
import json
from urlparse import urlparse



class AuthContainer:
    """
.. class:: AuthContainer
    """
    FILENAME = ""
    """
    str: correspending file
    """
    CREDENTIALS = {}
    """
    dict: authentication credentials
    """

    def __init__(self, filename):
        """
        Constructor, creating the class. It requires specifying a filename.
        If the file already exists, already existing entries are imported.

        :param filename: filename
        :type filename: str
        """
        self.FILENAME = filename
        try:
            self.__import()
        except ValueError:
            pass



    def __import(self):
        """This function imports definitions from the file."""
        global CREDENTIALS

        if os.path.exists(self.FILENAME) and \
            oct(stat.S_IMODE(os.lstat(self.FILENAME).st_mode)) == "0600":
            #loading file
            self.CREDENTIALS = json.loads(self.get_json(self.FILENAME))
        else:
            raise ValueError("File non-existent or file mode not 0600!")



    def get_json(self, filename):
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


    def save(self):
        """
        This function stores the changed authentication container to disk.
        """
        try:
            with open(self.FILENAME, 'w') as target:
                target.write(json.dumps(self.CREDENTIALS))

            #setting the good perms
            os.chmod(self.FILENAME, 0600)
        except IOError as err:
            raise err



    def __manage_credentials(self, hostname, username, password,
        remove_entry=False):
        """
        This functions adds or removes credentials to/from the authentication
        container.
        Adding credentials requires a hostname, username and corresponding
        password. Removing credentials only requires a hostname.

        There are two alias functions for credentials management:
        add_credentials() and remove_credentials()

        :param hostname: hostname
        :type hostname: str
        :param username: username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param remove_entry: setting True will remove an entry
        :type remove_entry: bool
        """
        global CREDENTIALS
        hostname = self.cut_hostname(hostname)

        try:
            if remove_entry:
                #remove entry
                del self.CREDENTIALS[hostname]
            else:
                #add entry
                self.CREDENTIALS[hostname] = {}
                self.CREDENTIALS[hostname]["username"] = username
                self.CREDENTIALS[hostname]["password"] = password
        except KeyError:
            pass

    #aliases
    def add_credentials(self, hostname, username, password):
        """
        Adds credentials to the authentication container.

        :param hostname: hostname
        :type hostname: str
        :param username: username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        return self.__manage_credentials(hostname, username, password)

    def remove_credentials(self, hostname):
        """
        Removes credentials from the authentication container.

        :param hostname: hostname
        :type hostname: str
        """
        return self.__manage_credentials(hostname, "", "", True)



    def get_hostnames(self):
        """This function returns hostnames"""
        return self.CREDENTIALS.keys()



    @staticmethod
    def cut_hostname(snippet):
        """
        This function removes protocol pre- and postfix data in order to
        find/create generic authentication information.

        :param snippet: connection string, URI/URL,...
        :type snippet: str
        """
        parsed_uri = urlparse(snippet)
        host = '{uri.netloc}'.format(uri=parsed_uri)
        if host == "":
            #non-URL/URI
            host = snippet
        return host



    def get_credential(self, hostname):
        """
        This function returns credentials for a particular hostname.
        
        :param hostname: hostname
        :type hostname: str
        """
        hostname = self.cut_hostname(hostname)
        try:
            return (
                self.CREDENTIALS[hostname]["username"],
                self.CREDENTIALS[hostname]["password"]
                )
        except KeyError:
            pass
