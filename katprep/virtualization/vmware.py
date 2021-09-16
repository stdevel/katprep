# -*- coding: utf-8 -*-
"""
Class for sending requests to pyvmomi as libvirt is still
just an endless pain when managing VMware products
"""

import logging
import ssl
import sys

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from .base import PowerManager, SnapshotManager
from ..connector import BaseConnector
from ..exceptions import (EmptySetException, InvalidCredentialsException,
SessionException, SnapshotExistsException)
from ..network import is_ipv4, is_ipv6

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class PyvmomiClient(BaseConnector, SnapshotManager, PowerManager):
    """
.. class:: PyvmomiClient
    """
    LOGGER = logging.getLogger('PyvmomiClient')
    """
    logging: Logger instance
    """

    def __init__(self, log_level, hostname, username, password):
        """
        Constructor, creating the class. It requires specifying a URI and
        a username and password for communicating with the hypervisor.
        The constructor will throw an exception if an invalid libvirt URI
        was specified. After initialization, a connection is established
        automatically.

        :param log_level: log level
        :type log_level: logging
        :param hostname: hostname
        :type hostname: str
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        """
        #set logging
        self.LOGGER.setLevel(log_level)
        #set custom port
        parsed_uri = urlparse(hostname)
        host = '{uri.path}'.format(uri=parsed_uri)
        if ":" in host:
            self.HOSTNAME, self.PORT = host.split(':', 1)
        else:
            self.HOSTNAME = hostname
            self.PORT = 443

        super().__init__(username, password)

    def _connect(self):
        """This function establishes a connection to the hypervisor."""
        context = None
        #skip SSL verification for now
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
        #try to connect
        try:
            self._session = SmartConnect(
                host=self.HOSTNAME,
                user=self._username, pwd=self._password,
                port=self.PORT, sslContext=context
            )
        except vim.fault.InvalidLogin:
            raise InvalidCredentialsException("Invalid credentials")



    def __get_obj(self, content, vimtype, name):
        """
        Gets the vSphere object associated with a given text name

        :param content: Session content
        :type content: SI session
        :param vimtype: Internal pyvmomi type
        :type vimtype: pyvmomi type
        :param name: object name
        :type name: str
        """
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True
        )
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

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
        :param snapshot_text: Snapshot text
        :type snapshot_text: str
        :param action: The action to perform. create, remove or revert.
        :type remove_snapshot: str

        """
        #make sure to quiesce and not dump memory
        #TODO: maybe we should supply an option for this?
        dump_memory = False
        quiesce = True
        vm_name = host.virtualisation_id
        try:
            content = self._session.RetrieveContent()
            vm = self.__get_obj(content, [vim.VirtualMachine], vm_name)
            if action.lower() == "revert":
                #TODO: implement revert
                raise NotImplementedError("Reverting snapshots not supported")
            elif action.lower() == "remove":
                #get _all_ the snapshots
                snapshots = self.__get_snapshots(vm_name)
                for snapshot in snapshots:
                    childs = snapshot.childSnapshotList
                    if snapshot.name == snapshot_title:
                        if action.lower() == "remove":
                            #remove snapshot
                            snapshot.snapshot.RemoveSnapshot_Task(True)
                        else:
                            #revert snapshot
                            snapshot.snapshot.RevertToSnapshot_Task()
                    if childs:
                        #also iterate through childs
                        for child in childs:
                            if child.name == snapshot_title:
                                if action.lower() == "remove":
                                    #remove snapshot
                                    child.snapshot.RemoveSnapshot_Task(True)
                                else:
                                    #revert snapshot
                                    child.snapshot.RevertToSnapshot_Task()
            else:
                #only create snapshot if not already existing
                try:
                    if not self.has_snapshot(vm_name, snapshot_title):
                        task = vm.CreateSnapshot(
                            snapshot_title, snapshot_text, dump_memory, quiesce
                        )
                    else:
                        raise SnapshotExistsException(
                            f"Snapshot {snapshot_title!r} for VM {vm_name!r} already exists!"
                        )
                except EmptySetException as err:
                    task = vm.CreateSnapshot(
                        snapshot_title, snapshot_text, dump_memory, quiesce
                    )

        except (TypeError, ValueError, AttributeError) as err:
            raise SessionException(
                "Unable to manage snapshot: '{}'".format(err)
            ) from err

    def __get_snapshots(self, vm_name):
        """
        Returns a set of all snapshots for a particular VM.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        try:
            content = self._session.RetrieveContent()
            container = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True
            )
            for c in container.view:
                if c.name == vm_name:
                    snapshots = c.snapshot.rootSnapshotList
                    return snapshots
        except AttributeError:
            raise EmptySetException("No snapshots found")

    def has_snapshot(self, host, snapshot_title):
        """
        Returns whether a particular virtual machine is currently protected
        by a snapshot. This requires specifying a VM name.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        #get _all_ the snapshots
        snapshots = self.__get_snapshots(host.virtualisation_id)
        try:
            for snapshot in snapshots:
                childs = snapshot.childSnapshotList
                if snapshot.name == snapshot_title:
                    return True
                #also check childs
                elif childs:
                    for child in childs:
                        if child.name == snapshot_title:
                            return True
            raise EmptySetException("No snapshots found")
        except TypeError:
            #no snapshots
            raise EmptySetException("No snapshots found")



    def get_vm_ips(self, hide_empty=True, ipv6_only=False):
        """
        Returns a list of VMs and their IPs available through the current
        connection.

        :param hide_empty: hide VMs without network information
        :type hide_empty: bool
        :param ipv6_only: use IPv6 addresses only
        :type ipv6_only: bool
        """
        try:
            #get _all_ the VMs
            content = self._session.RetrieveContent()
            #result = {}
            result = []
            #create view cotaining VM objects
            object_view = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True
            )
            for obj in object_view.view:
                if not hide_empty or obj.summary.guest.ipAddress != None:
                    #try to find the best IP
                    self.LOGGER.debug("Trying to find best IP for VM '%s'", obj.name)
                    if ipv6_only:
                        is_valid_address = is_ipv6
                        self.LOGGER.debug("Filtering for IPv6")
                    else:
                        is_valid_address = is_ipv4
                        self.LOGGER.debug("Filtering for IPv4")

                    target_ip = obj.summary.guest.ipAddress
                    self.LOGGER.debug(
                        "Primary guest address: '%s'", target_ip
                    )

                    if not is_valid_address(target_ip):
                        # other NICs
                        for nic in obj.guest.net:
                            for address in nic.ipConfig.ipAddress:
                                if is_valid_address(address.ipAddress):
                                    target_ip = address.ipAddress
                                    self.LOGGER.debug(
                                        "NIC address: '%s'", target_ip
                                    )
                                    break

                            if is_valid_address(address.ipAddress):
                                break

                    self.LOGGER.debug(
                        "Set IP address to '%s'", target_ip
                    )

                    #Adding result
                    result.append(
                        {
                            "object_name": obj.config.name,
                            "hostname": obj.summary.guest.hostName,
                            "ip": target_ip
                        }
                    )
            return result
        except Exception as err:
            self.LOGGER.error("Unable to get VM IP information: '%s'", err)
            raise SessionException(err)



    def get_vm_hosts(self):
        """
        Returns a list of VMs and their hypervisors available through the
        current connection.
        """
        try:
            #get _all_ the VMs
            content = self._session.RetrieveContent()
            result = {}
            #create view cotaining VM objects
            object_view = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True
            )
            for obj in object_view.view:
                result[obj.config.name] = {
                    "hypervisor": obj.runtime.host.name
                }
            return result
        except ValueError as err:
            self.LOGGER.error("Unable to get VM hypervisor information: '%s'", err)
            raise SessionException(err)

    def restart_vm(self, host, force=False):
        """
        Restarts a particular VM (default: soft reboot using guest tools).

        :param host: Host to manage
        :type host: Host
        :param force: Flag whether a hard reboot is requested
        :type force: bool
        """
        try:
            #get VM
            content = self._session.RetrieveContent()
            vm = self.__get_obj(content, [vim.VirtualMachine], host.virtualisation_id)

            if force:
                #kill it with fire
                vm.ResetVM_Task()
            else:
                #killing me softly
                vm.RebootGuest()
        except:
            raise SessionException("Unable to restart VM: '{}'".format(
                sys.exc_info()[0]
            ))

    def _manage_power(
            self, host, action="poweroff"
        ):
        """
        Powers a particual virtual machine on/off forcefully.

        :param host: Host to manage
        :type host: Host
        :param action: action (poweroff, poweron)
        :type action: str
        """
        vm_name = host.virtualisation_id
        try:
            content = self._session.RetrieveContent()
            vm = self.__get_obj(content, [vim.VirtualMachine], vm_name)
            if action.lower() == "poweroff":
                #get down with the vickness
                task = vm.PowerOff()
            else:
                #fire it up
                task = vm.PowerOn()
        except AttributeError as err:
            raise SessionException(
                "Unable to manage power state: '{}'".format(err)
            )
        except ValueError as err:
            raise SessionException(
                "Unable to manage power state: '{}'".format(err)
            )


    def powerstate_vm(self, host):
        """
        Returns the power state of a particular virtual machine.

        :param host: Host to manage
        :type host: Host
        """
        vm_name = host.virtualisation_id
        try:
            content = self._session.RetrieveContent()
            vm = self.__get_obj(content, [vim.VirtualMachine], vm_name)
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                return "poweredOn"
            elif vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                return "poweredOff"
        except AttributeError as err:
            raise SessionException(
                "Unable to get power state: '{}'".format(err)
            )
        except ValueError as err:
            raise SessionException(
                "Unable to get power state: '{}'".format(err)
            )
