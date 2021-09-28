"""
Uyuni XMLRPC API client
"""

import logging
import ssl
from collections import namedtuple
from datetime import datetime
from xmlrpc.client import DateTime, Fault, ServerProxy

from ..connector import BaseConnector
from ..exceptions import (
    APILevelNotSupportedException,
    EmptySetException,
    InvalidCredentialsException,
    SessionException,
    SSLCertVerificationError,
)

NVREA = namedtuple("NVREA", "name version release epoch architecture")


def split_rpm_filename(filename: str):
    """
    Splits a standard style RPM file name into NVREA.
    It returns a name, version, release, epoch, arch, e.g.:
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, i386
        1:bar-9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64

    Proudly taken from:
    https://github.com/rpm-software-management/
    yum/blob/master/rpmUtils/miscutils.py

    :param filename: RPM file name
    :type filename: str
    :rtype: NVREA
    """

    if filename[-4:] == ".rpm":
        filename = filename[:-4]

    arch_index = filename.rfind(".")
    arch = filename[arch_index + 1:]

    rel_index = filename[:arch_index].rfind("-")
    rel = filename[rel_index + 1:arch_index]

    ver_index = filename[:rel_index].rfind("-")
    ver = filename[ver_index + 1:rel_index]

    epoch_index = filename.find(":")
    if epoch_index == -1:
        epoch = ""
    else:
        epoch = filename[:epoch_index]

    name = filename[epoch_index + 1:ver_index]
    return NVREA(name, ver, rel, epoch, arch)


class UyuniAPIClient(BaseConnector):
    """
    Class for communicating with the Uyuni API

    .. class:: UyuniAPIClient
    """

    LOGGER = logging.getLogger("UyuniAPIClient")
    """
    logging: Logger instance
    """
    API_MIN = 24
    """
    int: Minimum supported API version.
    """
    HEADERS = {"User-Agent": "katprep (https://github.com/stdevel/katprep)"}
    """
    dict: Default headers set for every HTTP request
    """

    def __init__(
            self, log_level, hostname, username, password,
            port=443, verify=True
    ):
        """
        Constructor creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param hostname: Uyuni host
        :type hostname: str
        :param port: HTTPS port
        :type port: int
        :param verify: SSL verification
        :type verify: bool
        """
        # set logging
        self.LOGGER.setLevel(log_level)
        self.LOGGER.debug(
            "About to create Uyuni client '%s'@'%s'",
            username, hostname
        )

        # set connection information
        self.LOGGER.debug("Set hostname to '%s'", hostname)
        self.url = "https://{0}:{1}/rpc/api".format(hostname, port)
        self.verify = verify

        # start session and check API version if Uyuni API
        self._api_key = None
        super().__init__(username, password)
        self.validate_api_support()

    def _connect(self):
        """
        This function establishes a connection to Uyuni.
        """
        # set API session and key
        try:
            if not self.verify:
                context = ssl._create_unverified_context()
            else:
                context = ssl.create_default_context()

            self._session = ServerProxy(self.url, context=context)
            self._api_key = self._session.auth.login(
                self._username, self._password
            )
        except ssl.SSLCertVerificationError as err:
            self.LOGGER.error(err)
            raise SSLCertVerificationError(str(err)) from err
        except Fault as err:
            if err.faultCode == 2950:
                raise InvalidCredentialsException(
                    f"Wrong credentials supplied: {err.faultString!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def validate_api_support(self):
        """
        Checks whether the API version on the Uyuni server is supported.
        Using older versions than API_MIN is not recommended. In this case, an
        exception will be thrown.

        :raises: APILevelNotSupportedException
        """
        try:
            # check whether API is supported
            api_level = self._session.api.getVersion()
            if float(api_level) < self.API_MIN:
                raise APILevelNotSupportedException(
                    f"Your API version ({api_level!r}) doesn't support"
                    "required calls."
                    f"You'll need API version ({self.API_MIN!r}) or higher!"
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
                return [x["id"] for x in hosts]
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_id(self, hostname):
        """
        Returns the profile ID of a particular system

        :param hostname: System hostname
        :type hostname: str
        """
        try:
            host_id = self._session.system.getId(
                self._api_key, hostname
            )
            if host_id:
                return host_id[0]["id"]
            raise EmptySetException(
                f"System not found: {hostname!r}"
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {hostname!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_params(self, system_id):
        """
        Returns the parameters of a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            params = self._session.system.getCustomValues(
                self._api_key, system_id
            )
            return params
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_owner(self, system_id):
        """
        Returns the host owner

        :param system_id: profile ID
        :type system_id: int
        """
        host_params = self.get_host_params(system_id)
        try:
            return host_params['katprep_owner']
        except KeyError:
            raise SessionException(
                f"Owner not found for {system_id!r}"
            )

    def get_host_patches(self, system_id):
        """
        Returns available patches for a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            errata = self._session.system.getRelevantErrata(
                self._api_key, system_id
            )
            return errata
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_patch_by_name(self, patch_name):
        """
        Returns a patch by name

        :param patch_name: Patch name (e.g. openSUSE-2020-1001)
        :type patch_name: str
        """
        try:
            patch = self._session.errata.getDetails(
                self._api_key, patch_name
            )
            return patch
        except Fault as err:
            if "no such patch" in err.faultString.lower():
                raise EmptySetException(
                    f"Patch not found: {patch_name!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_package_by_file_name(self, file_name):
        """
        Returns a package by file name

        :param file_name: file name (e.g. foo-1.0-1.i386.rpm)
        :type file_name: str
        """
        package_nvrea = split_rpm_filename(file_name)

        try:
            package = self._session.packages.findByNvrea(
                self._api_key,
                package_nvrea.name,
                package_nvrea.version,
                package_nvrea.release,
                package_nvrea.epoch,
                package_nvrea.architecture
            )
            return package
        except Fault as err:
            if "no such package" in err.faultString.lower():
                raise EmptySetException(
                    f"Package not found: {file_name!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_upgrades(self, system_id):
        """
        Returns available package upgrades

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
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
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_groups(self, system_id):
        """
        Returns groups for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            groups = self._session.system.listGroups(
                self._api_key, system_id
            )
            return groups
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_details(self, system_id):
        """
        Returns details for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            details = self._session.system.getDetails(
                self._api_key, system_id
            )
            return details
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_network(self, system_id):
        """
        Returns network information for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            details = self._session.system.getNetwork(
                self._api_key, system_id
            )
            return details
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def install_patches(self, system_id, patches):
        """
        Install patches on a given system

        :param system_id: profile ID
        :type system_id: int
        :param patches: patch IDs
        :type patches: int[]
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
                    f"System not found: {system_id!r}"
                )
            if "invalid errata" in err.faultString.lower():
                raise EmptySetException(
                    f"Errata not found: {err.faultString!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def install_upgrades(self, system_id, upgrades):
        """
        Install package upgrades on a given system

        :param system_id: profile ID
        :type system_id: int
        :param upgrades: package IDs
        :type upgrades: int[]
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
            # returning an array to be consistent with install_patches
            return [action_id]
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            if "cannot find package" in err.faultString.lower():
                raise EmptySetException(
                    f"Upgrade not found: {err.faultString!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def host_reboot(self, system_id):
        """
        Reboots a system immediately

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.system.scheduleReboot(
                self._api_key, system_id,
                DateTime(datetime.now().timetuple())
            )
            return action_id
        except Fault as err:
            if "could not find server" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_action(self, system_id, task_id):
        """
        Retrieves information about a particular host action

        :param system_id: profile ID
        :type system_id: int
        :param task_id: task ID
        :type task_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )
        if not isinstance(task_id, int):
            raise EmptySetException(
                "No task found - use task IDs"
            )

        try:
            # return particular action
            actions = self.get_host_actions(system_id)
            action = [x for x in actions if x['id'] == task_id]
            if not action:
                raise EmptySetException("Action not found")
            return action
        except Fault as err:
            if "action not found" in err.faultString.lower():
                raise EmptySetException(
                    f"Action not found: {task_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_actions(self, system_id):
        """
        Returns actions for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            actions = self._session.system.listSystemEvents(
                self._api_key, system_id
            )
            return actions
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_user(self, user_name):
        """
        Retrieves information about a particular user

        :param user_name: Username
        :type user_name: str
        """
        if not isinstance(user_name, str):
            raise EmptySetException(
                "No user found - use user name"
            )

        try:
            # return user information
            user_info = self._session.user.getDetails(
                self._api_key, user_name
            )
            return user_info
        except Fault as err:
            if "could not find user" in err.faultString.lower():
                raise EmptySetException(
                    f"User not found: {user_name!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_organization(self):
        """
        Retrieves current organization
        """
        return self.get_user(self._username)['org_name']

    def get_location(self):
        """
        Retrieves current location
        """
        # simply return the organization as Uyuni
        # does not support any kind of locations
        return self.get_organization()
