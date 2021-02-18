#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uyuni XMLRPC API client
"""

import logging
import ssl

from xmlrpc.client import ServerProxy, Fault, DateTime
from datetime import datetime
from .base import BaseConnector
from ..exceptions import (
    SessionException,
    InvalidCredentialsException,
    APILevelNotSupportedException,
    SSLCertVerificationError,
    EmptySetException,
)


class UyuniAPIClient(BaseConnector):
    """
    Class for communicating with the Uyuni API

    .. class:: UyuniAPIClient
    """

    LOGGER = logging.getLogger("UyuniAPIClient")
    """
    logging: Logger instance
    """
    API_MIN = 22
    """
    int: Minimum supported API version.
    """
    HEADERS = {"User-Agent": "katprep (https://github.com/stdevel/katprep)"}
    """
    dict: Default headers set for every HTTP request
    """
    skip_ssl = False
    """
    bool: Flag whether to ignore SSL verification
    """

    def __init__(
            self, log_level, username, password,
            hostname, port=443, skip_ssl=False
    ):
        """
        Constructor creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param hostname: Uyuni host
        :type hostname: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param port: HTTPS port
        :type port: int
        """
        # set logging
        logging.basicConfig(level=log_level)
        self.LOGGER.setLevel(log_level)
        self.LOGGER.debug(
            "About to create Uyuni client '%s'@'%s'",
            username, hostname
            )

        # set connection information
        self.LOGGER.debug("Set hostname to '%s'", hostname)
        self.url = "https://{0}:{1}/rpc/api".format(hostname, port)
        self.skip_ssl = skip_ssl

        # start session and check API version if Uyuni API
        self._api_key = None
        super().__init__(username, password)
        self.validate_api_support()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Destructor
        """
        self._session.auth.logout(self._api_key)

    def _connect(self):
        """
        This function establishes a connection to Uyuni.
        """
        # set API session and key
        try:
            if self.skip_ssl:
                context = ssl._create_unverified_context()
            else:
                context = ssl.create_default_context()

            self._session = ServerProxy(self.url, context=context)
            self._api_key = self._session.auth.login(
                self._username, self._password
            )
        except ssl.SSLCertVerificationError as err:
            self.LOGGER.error(err)
            raise SSLCertVerificationError
        except Fault as err:
            if err.faultCode == 2950:
                raise InvalidCredentialsException(
                    "Wrong credentials supplied: '%s'" % err.faultString
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def validate_api_support(self):
        """
        Checks whether the API version on the Uyuni server is supported.
        Using older versions than 24 is not recommended. In this case, an
        exception will be thrown.
        """
        try:
            # check whether API is supported
            api_level = self._session.api.getVersion()
            if float(api_level) < self.API_MIN:
                raise APILevelNotSupportedException(
                    "Your API version ({0}) doesn't support required calls."
                    "You'll need API version ({1}) or higher!".format(
                        api_level, self.API_MIN
                    )
                )
            self.LOGGER.info("Supported API version %s found.", api_level)
        except ValueError as err:
            self.LOGGER.error(err)
            raise APILevelNotSupportedException(
                "Unable to verify API version"
            )

    def get_hosts(self):
        """
        Returns all active system IDs
        """
        try:
            hosts = self._session.system.listActiveSystems(
                self._api_key
            )
            if hosts:
                _hosts = [x["id"] for x in hosts]
                return _hosts
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_id(self, hostname):
        """
        Returns the profile ID of a particular system
        """
        try:
            host_id = self._session.system.getId(
                self._api_key, hostname
            )
            if host_id:
                return host_id[0]["id"]
            raise EmptySetException(
                "System not found: '%s'" % hostname
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    "System not found: '%s'" % hostname
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_params(self, system_id):
        """
        Returns the parameters of a particular system
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            params = self._session.system.getCustomValues(
                self._api_key, system_id
            )
            return params
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_patches(self, system_id):
        """
        Returns available patches for a particular system
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            errata = self._session.system.getRelevantErrata(
                self._api_key, system_id
            )
            return errata
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_patch_by_name(self, patch_name):
        """
        Returns a patch by name
        """
        try:
            patch = self._session.errata.getDetails(
                self._api_key, patch_name
            )
            return patch
        except Fault as err:
            if "no such patch" in err.faultString.lower():
                raise EmptySetException(
                    "Patch not found: '%s'" % patch_name
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_upgrades(self, system_id):
        """
        Returns available package upgrades
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            packages = self._session.system.listLatestUpgradablePackages(
                self._api_key, system_id
            )
            _packages = []
            for pkg in packages:
                # exclude if it part of an errata
                erratum = self._session.packages.listProvidingErrata(
                    self._api_key, pkg["to_package_id"]
                )
                if not erratum:
                    _packages.append(pkg)
            return _packages
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_groups(self, system_id):
        """
        Returns groups for a given system
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            groups = self._session.system.listGroups(
                self._api_key, system_id
            )
            return groups
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_details(self, system_id):
        """
        Returns details for a given system
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            details = self._session.system.getDetails(
                self._api_key, system_id
            )
            return details
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def get_host_tasks(self, system_id):
        """
        Returns tasks for a given system
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            tasks = self._session.system.listSystemEvents(
                self._api_key, system_id
            )
            return tasks
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def install_patches(self, system_id, patches):
        """
        Install patches on a given system
        """
        try:
            # remove non-integer values
            _patches = [x for x in patches if isinstance(x, int)]
            if not _patches:
                raise EmptySetException(
                    "No patches supplied - use patch ID"
                )
            # install _all_ the patches
            action_id = self._session.system.scheduleApplyErrata(
                self._api_key, system_id, _patches
            )
            return action_id
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            if "invalid errata" in err.faultString.lower():
                raise EmptySetException(
                    "Errata not found: '%s'" % err.faultString
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def install_upgrades(self, system_id, upgrades):
        """
        Install package upgrades on a given system
        """
        try:
            # remove non-integer values
            _upgrades = [x for x in upgrades if isinstance(x, int)]
            if not _upgrades:
                raise EmptySetException(
                    "No upgrades supplied - use package ID"
                )
            # install _all_ the upgrades
            action_id = self._session.system.schedulePackageInstall(
                self._api_key, system_id, _upgrades,
                DateTime(datetime.now().timetuple())
            )
            return action_id
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    "System not found: '%s'" % system_id
                )
            if "cannot find package" in err.faultString.lower():
                raise EmptySetException(
                    "Upgrade not found: '%s'" % err.faultString
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    def host_reboot(self, system_id):
        """
        Reboots a system immediately
        """
        try:
            if not isinstance(system_id, int):
                raise EmptySetException(
                    "No system found - use system profile IDs"
                )
            action_id = self._session.system.scheduleReboot(
                self._api_key, system_id,
                DateTime(datetime.now().timetuple())
            )
            return action_id
        except Fault as err:
            if "could not find server" in err.faultString.lower():
                raise EmptySetException(
                    "System not found: '%s'" % system_id
                )
            raise SessionException(
                "Generic remote communication error: '%s'" % err.faultString
            )

    # TODO: task_get(self, task_id):