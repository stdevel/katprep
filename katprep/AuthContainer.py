"""
Class for managing multiple authentication credentials
"""

import logging
import os
import stat
import json
import base64
from collections import namedtuple
from urllib.parse import urlparse

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

Credentials = namedtuple('Credentials', 'username password')


class ContainerException(Exception):
    """
    Dummy class for authentication container errors

.. class:: ContainerException
    """
    pass



class AuthContainer:
    """
.. class:: AuthContainer
    """
    LOGGER = logging.getLogger('AuthContainer')
    """
    logging: Logger instance
    """

    def __init__(self, log_level, filename, key=""):
        """
        Constructor, creating the class. It requires specifying a filename.
        If the file already exists, already existing entries are imported.

        :param log_level: log level
        :type log_level: logging
        :param filename: filename
        :type filename: str
        :param key: The key used for encryption / decryption of secrets.
        :type key: str
        """
        self._encryption_marker = b"s/"

        self.CREDENTIALS = {}

        #set logging
        self.LOGGER.setLevel(log_level)
        #set key if defined
        self.KEY = ""
        if key:
            self.set_key(key)
        #set filename and import data
        self.FILENAME = filename
        try:
            self.__import()
        except FileNotFoundError:
            # file does not exist yet
            pass

    def set_key(self, key):
        """
        This function set or changes the key used for encryption/decryption.

        :param key: key
        :type key: str
        """
        try:
            key = key.zfill(32)
            key = key.encode()
            self.KEY = base64.urlsafe_b64encode(key)
        except ValueError as err:
            self.LOGGER.error("Empty password specified")

    def is_encrypted(self):
        """
        This functions returns whether the authentication container is
        encrypted.
        """
        if self.KEY:
            return True
        else:
            return False

    def __import(self):
        """This function imports definitions from the file."""
        try:
            self.CREDENTIALS = json.loads(self.get_json(self.FILENAME))
        except Exception as err:
            if not stat.S_IMODE(os.lstat(self.FILENAME).st_mode) == 0o0600:
                raise OSError("File mode of {!r} not 0600!".format(self.FILENAME))
            raise err

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
            self.LOGGER.error("Unable to read file '{}': '{}'".format(filename, err))

    def save(self):
        """
        This function stores the changed authentication container to disk.
        """
        try:
            with open(self.FILENAME, 'w') as target:
                target.write(json.dumps(self.CREDENTIALS))

            #setting the good perms
            os.chmod(self.FILENAME, 0o600)
        except IOError as err:
            raise ContainerException(err)



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
                #add encrypted or plain password
                if self.KEY:
                    crypto = Fernet(self.KEY.decode())
                    self.CREDENTIALS[hostname]["password"] = "s/{0}".format(
                        crypto.encrypt(password.encode()))
                else:
                    self.CREDENTIALS[hostname]["password"] = password
        except InvalidToken:
            raise ContainerException("Invalid password specified!")
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
        return list(self.CREDENTIALS.keys())

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
            credentials = self.CREDENTIALS[hostname]
            username = credentials["username"]
            password = credentials["password"]
        except KeyError as kerr:
            self.LOGGER.debug("Unable to retrieve credentials for {!r} ({})".format(hostname, kerr))
            return

        if self.is_encrypted():
            # Remove leading encryption marker
            password = password[len(self._encryption_marker):]

            try:
                crypto = Fernet(self.KEY)
                password = crypto.decrypt(password.encode())
            except InvalidToken:
                raise ContainerException("Invalid password specified!")

            password = password.decode()
        else:
            self.LOGGER.debug("Plain login data")

        return Credentials(username, password)
