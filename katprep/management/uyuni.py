"""
Uyuni XMLRPC API client
"""

import logging
import ssl
import base64
from datetime import datetime
from xmlrpc.client import DateTime, Fault, ServerProxy

from .utilities import split_rpm_filename
from ..connector import BaseConnector
from ..exceptions import (
    APILevelNotSupportedException,
    EmptySetException,
    InvalidCredentialsException,
    SessionException,
    SSLCertVerificationError,
    CustomVariableExistsException
)
from ..host import Upgrade


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
        This function establishes a connection to Uyuni
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
        Returns all system IDs
        """
        try:
            hosts = self._session.system.listSystems(
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

    def get_hosts_by_organization(self, organization):
        """
        Returns all systems by organisation
        """
        # filter not implemented by Uyuni API
        # simply return _all_ the hosts
        return self.get_hosts()

    def get_hosts_by_location(self, location):
        """
        Returns all systems by location
        """
        # filter not implemented by Uyuni API
        # simply return _all_ the hosts
        return self.get_hosts()

    def get_hosts_by_hostgroup(self, hostgroup):
        """
        Returns all systems by hostgroup
        """
        try:
            hosts = self._session.systemgroup.listSystems(
                self._api_key, hostgroup
            )
            if hosts:
                return [x["id"] for x in hosts]
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            if "unable to locate" in err.faultString.lower():
                raise EmptySetException(
                    "No systems found"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_host_id(self, hostname):
        """
        Returns the profile ID of a particular system

        :param hostname: system hostname
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

    def get_hostname_by_id(self, system_id):
        """
        Returns the hostname of a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        try:
            host = self._session.system.getName(
                self._api_key, system_id
            )
            return host["name"]
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
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

    def get_host_custom_variables(self, system_id):
        """
        Returns host custom variables (custom info key values)

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            values = self._session.system.getCustomValues(
                self._api_key, system_id
            )
            return values
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
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
            def missing_patch(error_message):
                message = error_message.lower()
                if ("no such patch" in message or
                    ("the patch" in message and "cannot be found" in message)):
                    return True

                return False

            if missing_patch(err.faultString):
                raise EmptySetException(
                    f"Patch not found: {patch_name!r}"
                ) from err

            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

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

            self.LOGGER.debug("Found %i upgrades for %s: %s", len(_packages), system_id, _packages)
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

    def install_plain_patches(self, host, patches=None):
        """
        Install patches on a given system

        :param host: The host on which to install updates
        :type host: Host
        :param patches: If given only installs the given patches.
        :type patches: list
        """
        # system_id = host.management_id
        # ensure that only integers are given
        # TODO: remove???
        # patches = [x for x in patches if isinstance(x, int)]
        if patches is None:
            patches = host.patches  # installing all patches

        # if not patches:
        #     raise EmptySetException(
        #         "No patches supplied - use patch IDs"
        #     )

        try:
            patches = [errata.id for errata in patches]
        except AttributeError as atterr:
            raise EmptySetException("Unable to get patch IDs") from atterr

        system_id = host.management_id

        try:
            action_id = self._session.system.scheduleApplyErrata(
                self._api_key, system_id, patches
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

    def install_plain_upgrades(self, host, upgrades=None):
        """
        Install package upgrades on a given system

        :param host: The host to upgrade
        :type host: Host
        :param upgrades: Specific upgrades to install
        :type upgrades: list
        """
        system_id = host.management_id

        if upgrades is None:
            upgrades = self.get_host_upgrades(system_id)
            upgrades = [Upgrade.from_dict(package) for package in upgrades]
        if not upgrades:
            self.LOGGER.debug("No upgrades for %s", host)
            return  # Nothing to do

        upgrade_ids = []
        try:
            for upgrade in upgrades:
                package_id = upgrade.package_id
                if package_id is None:
                    raise ValueError("{!r} has no valid package id set!".format(upgrade))

                upgrade_ids.append(package_id)
        except (TypeError, AttributeError, ValueError) as conversion_error:
            raise EmptySetException("Invalid package type") from conversion_error

        earliest_execution = DateTime(datetime.now().timetuple())

        try:
            action_id = self._session.system.schedulePackageInstall(
                self._api_key, system_id, upgrade_ids, earliest_execution
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

    def reboot_host(self, host):
        """
        Reboots a system

        :param host: host to reboot
        :type host: host object
        """
        if not (host.reboot_pre_script or host.reboot_post_script):
            # simply reboot host
            return self.plain_reboot_host(host)

        # We have pre-script or post-script
        system_id = host.management_id
        chain_label = f"{system_id}_reboot"
        self.add_actionchain(chain_label)
        action_ids = []
        if host.reboot_pre_script:
            action_ids.append(
                self.reboot_pre_script(host, chain_label)
            )

        # add reboot
        action_ids.append(
            self.actionchain_add_reboot(chain_label, system_id)
        )

        if host.reboot_post_script:
            action_ids.append(
                self.reboot_post_script(host, chain_label)
            )

        # schedule execution
        self.run_actionchain(chain_label)

        return action_ids

    def plain_reboot_host(self, host):
        """
        Reboots a system

        :param host: host to reboot
        :type host: host object
        """
        try:
            system_id = host.management_id
        except AttributeError as attrerr:
            raise EmptySetException(
                f"Unable to get management id from {host}"
            ) from attrerr

        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        earliest_execution = DateTime(datetime.now().timetuple())
        try:
            action_id = self._session.system.scheduleReboot(
                self._api_key, system_id, earliest_execution
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

        :param user_name: username
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

    def is_reboot_required(self, host):
        """
        Checks whether a particular host requires a reboot

        :param host: host
        :type host: host object
        """
        try:
            systems = self._session.system.listSuggestedReboot(
                self._api_key
            )

            return any(system["id"] == host.management_id for system in systems)
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_action_by_type(self, system_id, action_type):
        """
        Gets host action by specific type

        :param system_id: profile ID
        :type system_id: int
        :param action_type: action type
        :type action_type: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            actions = self._session.system.listSystemEvents(
                self._api_key, system_id, action_type
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

    def get_errata_task_status(self, system_id):
        """
        Get the status of errata installations for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Patch Update')

    def get_upgrade_task_status(self, system_id):
        """
        Get the status of package upgrades for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Package Install')

    def get_script_task_status(self, system_id):
        """
        Get the status of script executions for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Run an arbitrary script')

    def get_custom_variables(self):
        """
        Returns all defines custom variables (custom info keys)
        """
        try:
            _variables = self._session.system.custominfo.listAllKeys(
                self._api_key
            )
            variables = {x['label']: x['description'] for x in _variables}
            return variables
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def create_custom_variable(self, label, description):
        """
        Creates a custom variable (custom info keys)

        :param label: variable label
        :type label: str
        :param description: variable description
        :type label: str
        """
        try:
            self._session.system.custominfo.createKey(
                self._api_key, label, description
            )
        except Fault as err:
            if "already exists" in err.faultString.lower():
                raise CustomVariableExistsException(
                    f"Key already exists: {label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def update_custom_variable(self, label, description):
        """
        Updates a custom variable's description (custom info keys)

        :param label: variable label
        :type label: str
        :param description: variable description
        :type label: str
        """
        try:
            self._session.system.custominfo.updateKey(
                self._api_key, label, description
            )
        except Fault as err:
            if "does not exist" in err.faultString.lower():
                raise EmptySetException(
                    f"Key does not exist: {label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def delete_custom_variable(self, label):
        """
        Deletes a custom variable (custom info keys)

        :param label: variable label
        :type label: str
        """
        try:
            self._session.system.custominfo.deleteKey(
                self._api_key, label
            )
        except Fault as err:
            if "does not exist" in err.faultString.lower():
                raise EmptySetException(
                    f"Key does not exist: {label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def host_add_custom_variable(self, system_id, label, value):
        """
        Adds a custom variable to a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        :param value: variable value
        :type value: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            self._session.system.setCustomValues(
                self._api_key, system_id,
                {label: value}
            )
        except Fault as err:
            if "was not defined" in err.faultString.lower():
                raise EmptySetException(
                    f"Custom Variable does not exist: {label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def host_update_custom_variable(self, system_id, label, value):
        """
        Updates a custom variable for a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        :param value: variable value
        :type value: str
        """
        self.host_add_custom_variable(system_id, label, value)

    def host_delete_custom_variable(self, system_id, label):
        """
        Deletes a custom variable from a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            self._session.system.deleteCustomValues(
                self._api_key, system_id,
                [label]
            )
        except Fault as err:
            if "was not defined" in err.faultString.lower():
                raise EmptySetException(
                    f"Custom Variable does not exist: {label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def host_run_command(self, system_id, command, user="root", group="root"):
        """
        Runs a particular command on a host

        :param system_id: profile ID
        :type system_id: int
        :param command: command
        :type command: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        earliest_execution = DateTime(datetime.now().timetuple())
        # add shebang if not found
        if not command.startswith("#!/"):
            command = f'#!/bin/sh\n{command}'

        try:
            return self._session.system.scheduleScriptRun(
                self._api_key,
                system_id,
                user,
                group,
                600,
                command,
                earliest_execution
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_actionchains(self):
        """
        Returns all defined action chains
        """
        try:
            return self._session.actionchain.listChains(
                self._api_key
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def get_actionchain_actions(self, chain_label):
        """
        Returns actions of a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            actions = self._session.actionchain.listChainActions(
                self._api_key, chain_label
            )
            if len(actions) == 0:
                raise EmptySetException("Action chain is empty")
            return actions
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def add_actionchain(self, label):
        """
        Creates a new action chain

        :param label: action chain label
        :type label: str
        """
        try:
            chain_id = self._session.actionchain.createChain(
                self._api_key, label
            )
            return chain_id
        except Fault as err:
            if "is missing" in err.faultString.lower():
                raise EmptySetException(
                    "Label missing"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def run_actionchain(self, chain_label):
        """
        Runs a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            earliest_execution = DateTime(datetime.now().timetuple())
            chain_id = self._session.actionchain.scheduleChain(
                self._api_key, chain_label, earliest_execution
            )
            return chain_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def delete_actionchain(self, chain_label):
        """
        Removes a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            self._session.actionchain.deleteChain(
                self._api_key, chain_label
            )
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def actionchain_add_patches(self, chain_label, system_id, patches):
        """
        Adds patch installation to an action chain

        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param patches: patch IDs
        :type patches: int array
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.actionchain.addErrataUpdate(
                self._api_key, system_id, patches, chain_label
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            if "could not find errata" in err.faultString.lower():
                raise EmptySetException(
                    f"At least one patch not found: {patches!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def actionchain_add_upgrades(self, chain_label, system_id, upgrades):
        """
        Adds package upgrad to an action chain

        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param upgrades: upgrade IDs
        :type upgrades: int array
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.actionchain.addPackageUpgrade(
                self._api_key, system_id, upgrades, chain_label
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            if "invalid package" in err.faultString.lower():
                raise EmptySetException(
                    f"At least one package upgrade not found: {upgrades!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def actionchain_add_command(self, chain_label, system_id, command, user="root", group="root"):
        """
        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param command: command
        :type command: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )
        if len(command) == 0:
            raise EmptySetException(
                "Command is empty"
            )
        # add shebang if not found
        if not command.startswith("#!/"):
            command = f'#!/bin/sh\n{command}'

        try:
            action_id = self._session.actionchain.addScriptRun(
                self._api_key,
                system_id,
                chain_label,
                user,
                group,
                600,
                str(
                    base64.b64encode(command.encode("utf-8")),
                    "utf-8"
                )
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def actionchain_add_reboot(self, chain_label, system_id):
        """
        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.actionchain.addSystemReboot(
                self._api_key,
                system_id,
                chain_label,
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                )
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            )

    def install_patches(self, host, patches):
        """
        Installs patches

        :param host: host on which to install updates
        :type host: host object
        :param patches: patch IDs
        :type patches: int array
        """
        if not (host.patch_pre_script or host.patch_post_script):
            return self.install_plain_patches(host, patches)

        # We have a pre or post-script and work with an action chain
        system_id = host.management_id
        chain_label = f"{system_id}_patch"
        self.add_actionchain(chain_label)
        action_ids = []

        if host.patch_pre_script:
            action_ids.append(
                self.install_pre_script(host, chain_label)
            )

        # add patches
        action_ids.append(
            self.actionchain_add_patches(chain_label, system_id, patches)
        )

        if host.patch_post_script:
            action_ids.append(
                self.install_post_script(host, chain_label)
            )

        # schedule execution
        self.run_actionchain(chain_label)

        return action_ids

    def install_upgrades(self, host, upgrades):
        """
        Installs upgrades

        :param system_id: profile ID
        :type system_id: int
        :param upgrades: package IDs
        :type upgrade: int array
        """
        if not (host.patch_pre_script or host.patch_post_script):
            # simply install patches
            return self.install_plain_upgrades(host, upgrades)

        # We have pre-script or post-script
        system_id = host.management_id
        chain_label = f"{system_id}_upgrade"
        self.add_actionchain(chain_label)
        action_ids = []
        if host.patch_pre_script:
            action_ids.append(
                self.install_pre_script(host, chain_label)
            )

        # add upgrades
        action_ids.append(
            self.actionchain_add_upgrades(chain_label, system_id, upgrades)
        )

        if host.patch_post_script:
            action_ids.append(
                self.install_post_script(host, chain_label)
            )

        # schedule execution
        self.run_actionchain(chain_label)

        return action_ids

    def install_pre_script(self, host, chain_label):
        """
        Runs the install pre-script

        :param system_id: profile ID
        :type system_id: int
        :param chain_label: chain label
        :type chain_label: str
        """
        return self.actionchain_add_command(
            chain_label,
            host.management_id,
            host.patch_pre_script,
            user=host.patch_pre_script_user,
            group=host.patch_pre_script_group
        )

    def install_post_script(self, host, chain_label):
        """
        Runs the install post-script

        :param system_id: profile ID
        :type system_id: int
        :param chain_label: chain label
        :type chain_label: str
        """
        return self.actionchain_add_command(
            chain_label,
            host.management_id,
            host.patch_post_script,
            user=host.patch_post_script_user,
            group=host.patch_post_script_group
        )

    def reboot_pre_script(self, host, chain_label):
        """
        Runs the reboot pre-script

        :param system_id: profile ID
        :type system_id: int
        :param chain_label: chain label
        :type chain_label: str
        """
        return self.actionchain_add_command(
            chain_label,
            host.management_id,
            host.reboot_pre_script,
            user=host.reboot_pre_script_user,
            group=host.reboot_pre_script_group
        )

    def reboot_post_script(self, host, chain_label):
        """
        Runs the reboot post-script

        :param system_id: profile ID
        :type system_id: int
        :param chain_label: chain label
        :type chain_label: str
        """
        return self.actionchain_add_command(
            chain_label,
            host.management_id,
            host.reboot_post_script,
            user=host.reboot_post_script_user,
            group=host.reboot_post_script_group
        )
