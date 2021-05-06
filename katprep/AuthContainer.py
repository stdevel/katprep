"""
Class for managing multiple authentication credentials
"""

import logging
import os
import stat
import json
import base64
import sys
from collections import namedtuple
from urllib.parse import urlparse

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

Credentials = namedtuple("Credentials", "username password")


class ContainerException(Exception):
    """
        Dummy class for authentication container errors

    .. class:: ContainerException
    """


class AuthContainer:
    """
    .. class:: AuthContainer
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
        self.__credentials = {}
        self._encryption_marker = b"s/"

        self.LOGGER = logging.getLogger("AuthContainer")
        self.LOGGER.setLevel(log_level)

        self.__key = None
        self.set_key(key)

        self._filename = filename
        try:
            self._import()
        except FileNotFoundError:
            # file does not exist yet
            pass

    def set_key(self, key):
        """
        This function set or changes the key used for encryption/decryption.

        :param key: key
        :type key: str
        """
        if not key:
            return

        assert isinstance(key, str)
        key = key.zfill(32)[-32:]
        key = key.encode()
        self.__key = base64.urlsafe_b64encode(key)

    def is_encrypted(self):
        """
        This functions returns whether the authentication container is
        encrypted.
        """
        return bool(self.__key)

    def _import(self):
        """This function imports definitions from the file."""

        if os.path.exists(self._filename):
            if sys.platform != 'win32':
                # Windows might not allow for setting 600

                if stat.S_IMODE(os.lstat(self._filename).st_mode) != 0o0600:
                    raise OSError("File mode of {!r} not 0600!".format(self._filename))

        try:
            self.__credentials = json.loads(self._get_json())
        except Exception as err:
            raise err

    def _get_json(self):
        """
        Reads a JSON file and returns the whole content as one-liner.

        :param filename: the JSON filename
        :type filename: str
        """
        filename = self._filename

        try:
            with open(filename, "r") as json_file:
                json_data = json_file.read().replace("\n", "")
            return json_data
        except FileNotFoundError as err:
            self.LOGGER.debug("File {!r} is missing: {}".format(filename, err))
            # Load empty config
            return '{}'
        except IOError as err:
            self.LOGGER.error(
                "Unable to read file {!r}: {}".format(filename, err)
            )
            raise err

    def save(self):
        """
        This function stores the changed authentication container to disk.
        """
        try:
            with open(self._filename, "w") as target:
                target.write(json.dumps(self.__credentials))

            # setting the good perms
            os.chmod(self._filename, 0o600)
        except IOError as err:
            raise ContainerException(err)

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
        if not isinstance(password, str):
            raise TypeError(
                "Expecting password as a str instead of {}".format(
                    type(password)
                )
            )

        hostname = self.cut_hostname(hostname)

        if self.__key:
            try:
                crypto = Fernet(self.__key)
                password = crypto.encrypt(password.encode())
                password = self._encryption_marker + password
                password = password.decode()
            except InvalidToken:
                raise ContainerException("Invalid password specified!")

        self.__credentials[hostname] = {
            "username": username,
            "password": password,
        }

    def remove_credentials(self, hostname):
        """
        Removes credentials from the authentication container.

        :param hostname: hostname
        :type hostname: str
        """
        hostname = self.cut_hostname(hostname)

        try:
            del self.__credentials[hostname]
        except KeyError:
            pass

    def get_hostnames(self):
        """This function returns hostnames"""
        return list(self.__credentials.keys())

    @staticmethod
    def cut_hostname(snippet):
        """
        This function removes protocol pre- and postfix data in order to
        find/create generic authentication information.

        :param snippet: connection string, URI/URL,...
        :type snippet: str
        """
        parsed_uri = urlparse(snippet)
        host = str(parsed_uri.netloc)
        if host == "":
            # non-URL/URI
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
            credentials = self.__credentials[hostname]
            username = credentials["username"]
            password = credentials["password"]
        except KeyError as kerr:
            self.LOGGER.debug(
                "Unable to retrieve credentials for {!r} ({})".format(
                    hostname, kerr
                )
            )
            return

        if self.is_encrypted():
            # Remove leading encryption marker
            password = password[len(self._encryption_marker):]

            try:
                crypto = Fernet(self.__key)
                password = crypto.decrypt(password.encode())
            except InvalidToken:
                raise ContainerException("Invalid password specified!")

            password = password.decode()
        else:
            self.LOGGER.debug("Plain login data")

        return Credentials(username, password)
