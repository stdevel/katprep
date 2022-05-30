# -*- coding: utf-8 -*-
"""
Class for sending requests to libvirt
"""

import logging
import socket

import libvirt

from .base import PowerManager, SnapshotManager
from ..connector import BaseConnector
from ..exceptions import (EmptySetException, InvalidCredentialsException,
SessionException, UnsupportedRequestException)


class LibvirtClient(BaseConnector, SnapshotManager, PowerManager):
    """
    Class for communicating with libvirt

.. class:: LibvirtClient
    """
    LOGGER = logging.getLogger('LibvirtClient')
    """
    logging: Logger instance
    """

    def __init__(self, log_level, uri, username, password):
        """
        Constructor, creating the class. It requires specifying a URI and
        a username and password for communicating with the hypervisor.
        The constructor will throw an exception if an invalid libvirt URI
        was specified. After initialization, a connection is established
        automatically.

        :param log_level: log level
        :type log_level: logging
        :param uri: libvirt URI
        :type uri: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        #set logging
        self.LOGGER.setLevel(log_level)
        #validate and set URI
        if self.validate_uri(uri):
            self.URI = uri
        else:
            raise SessionException("Invalid URI string specified!")

        super().__init__(username, password)

    @staticmethod
    def validate_uri(uri):
        """
        Verifies a libvirt URI and throws an exception if the URI is invalid.
        This is done by checking if the URI contains one of the well-known
        libvirt protocols.

        :param uri: a libvirt URI
        :type uri: str
        """
        if "://" not in uri:
            return False

        prefixes = {
            "lxc", "qemu", "xen", "hyperv", "vbox", "openvz", "uml", "phyp",
            "vz", "bhyve", "esx", "vpx", "vmwareplayer", "vmwarews",
            "vmwarefusion"
        }

        # check whether a valid prefix was found
        return any(uri.startswith(prefix) for prefix in prefixes)

    def _connect(self):
        """This function establishes a connection to the hypervisor."""
        #create weirdo auth dict
        auth = [
            [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
            self.retrieve_credentials, None
            ]
        #authenticate
        try:
            self._session = libvirt.openAuth(self.URI, auth, 0)
            if not self._session:
                raise SessionException("Unable to establish connection to hypervisor!")
        except libvirt.libvirtError as err:
            raise InvalidCredentialsException("Invalid credentials")



    def retrieve_credentials(self, credentials, user_data):
        """
        Retrieves the libvirt credentials in a strange format and hand it to
        the API in order to communicate with the hypervisor.
        To be honest, I have no idea why this has to be done this way. I have
        taken this function from the official libvirt documentation.

        :param credentials: libvirt credentials object
        :param user_data: some data that will never be used
        :type user_data: None
        """
        #get credentials for libvirt
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = self._username
                if len(credential[4]) == 0:
                    credential[4] = credential[3]
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = self._password
            else:
                return -1
        return 0

    def _manage_snapshot(
            self, host, snapshot_title, snapshot_text, action="create"
        ):
        """
        Creates/removes a snapshot for a particular virtual machine.
        This requires specifying a VM, comment title and text.
        There are also two alias functions.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Descriptive text for the snapshot
        :type snapshot_text: str
        :param action: The action to perform. create, remove or revert.
        :type action: str
        """
        try:
            target_vm = self._session.lookupByName(host.virtualisation_id)
            if action.lower() == "remove":
                #remove snapshot
                target_snap = target_vm.snapshotLookupByName(snapshot_title, 0)
                return target_snap.delete(0)
            elif action.lower() == "revert":
                #revert snapshot
                target_snap = target_vm.snapshotLookupByName(snapshot_title, 0)
                return target_vm.revertToSnapshot(target_snap)
            else:
                #create snapshot
                snap_xml = """<domainsnapshot><name>{}</name><description>{}
                    "</description></domainsnapshot>""".format(
                        snapshot_title, snapshot_text
                    )
                return target_vm.snapshotCreateXML(snap_xml, 0)
        except libvirt.libvirtError as err:
            raise SessionException("Unable to {} snapshot: '{}'".format(
                action.lower(), err)
            )

    def has_snapshot(self, host, snapshot_title):
        """
        Returns whether a particular virtual machine is currently protected
        by a snapshot. This requires specifying a VM name.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        try:
            #find VM and get all snapshots
            target_vm = self._session.lookupByName(host.virtualisation_id)
            target_snapshots = target_vm.snapshotListNames(0)
            if snapshot_title in target_snapshots:
                return True
        except libvirt.libvirtError as err:
            if "no domain with name" in err.message.lower():
                #snapshot not found
                raise EmptySetException("No snapshots found")
            else:
                self.LOGGER.error("Unable to determine snapshot: '{}'".format(err))
                raise SessionException(err)



    def get_vm_ips(self):
        """
        Returns a list of VMs and their IPs available through the current
        connection.
        """
        try:
            #get all VMs
            vms = self._session.listDefinedDomains()
            result = []

            #scan _all_ the VMs
            for vm in vms:
                #get VM and lookup hostname
                target_vm = self._session.lookupByName(vm)
                target_hostname = target_vm.hostname()
                #lookup IP
                #TODO: IPv6 only?
                target_ip = socket.gethostbyname(target_hostname)
                result.append(
                    {"hostname": target_hostname, "ip": target_ip}
                )
            return result
        except libvirt.libvirtError as err:
            if "not supported by" in err.message.lower():
                raise UnsupportedRequestException(err)
            else:
                raise SessionException("Unable to get VM IP information: '{}'".format(err))



    def get_vm_hosts(self):
        """
        Returns a list of VMs and their hypervisors available through the
        current connection.
        """
        raise NotImplementedError("get_vm_hosts hasn't been implemented yet")

    def restart_vm(self, host, force=False):
        """
        Restarts a particular VM (default: soft reboot using guest tools).

        :param host: Host to manage
        :type host: Host
        :param force: Flag whether a hard reboot is requested
        :type force: bool
        """
        try:
            target_vm = self._session.lookupByName(host.virtualisation_id)
            if force:
                #kill it with fire
                target_vm.reboot(1)
            else:
                #killing me softly
                target_vm.reboot(0)
        except libvirt.libvirtError as err:
            if "unsupported flags" in err.message.lower():
                #trying hypervisor default
                target_vm.reboot(0)
                self.LOGGER.error(
                    "Forcing reboot impossible, trying hypervisor default")
            else:
                raise SessionException("Unable to restart VM: '{}'".format(err))


    def powerstate_vm(self, host):
        """
        Returns the power state of a particular virtual machine.

        :param host: Host to manage
        :type host: Host
        """
        raise NotImplementedError("powerstate_vm hasn't been implemented yet")

    def _manage_power(self, host, action="poweroff"):
        """
        Powers a particual virtual machine on/off forcefully.

        :param host: Host to manage
        :type host: Host
        :param action: action (poweroff, poweron)
        :type action: str
        """
        raise NotImplementedError("_manage_power hasn't been implemented yet")
