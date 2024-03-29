# -*- coding: utf-8 -*-
"""
Base for creating management classes.
"""

from abc import ABCMeta, abstractmethod


class BaseConnector(metaclass=ABCMeta):
    """
    Basic management connector that connects on creation.
    """

    def __init__(self, username, password, **kwargs):
        self._username = username
        self._password = password
        self._session = None
        self._connect()

    @abstractmethod
    def _connect(self):
        pass


class SnapshotManager(metaclass=ABCMeta):
    """
    Managers with snapshot support.

    This base class provides a general interface for manager classes
    that support the use of snapshots.
    """

    @abstractmethod
    def _manage_snapshot(self, vm_name, snapshot_title, snapshot_text, action="create"):
        """
        Helper function to perform creating, reverting or removing a snapshot.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Descriptive text for the snapshot
        :type snapshot_text: str
        :param action: The action to perform. create, remove or revert.
        :type action: str
        """

    @abstractmethod
    def has_snapshot(self, vm_name, snapshot_title):
        """
        Returns whether a particular virtual machine is currently protected
        by a snapshot. This requires specifying a VM name.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """

    def create_snapshot(self, vm_name, snapshot_title, snapshot_text):
        """
        Creates a snapshot for a particular virtual machine.
        This requires specifying a VM, comment title and text.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Descriptive text for the snapshot
        :type snapshot_text: str
        """
        return self._manage_snapshot(
            vm_name, snapshot_title, snapshot_text, action="create"
        )

    def remove_snapshot(self, vm_name, snapshot_title):
        """
        Removes a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self._manage_snapshot(vm_name, snapshot_title, "", action="remove")

    def revert_snapshot(self, vm_name, snapshot_title):
        """
        Reverts to  a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self._manage_snapshot(vm_name, snapshot_title, "", action="revert")


class PowerManager(metaclass=ABCMeta):
    @abstractmethod
    def _manage_power(self, vm_name, action="poweroff"):
        """
        Powers a particual virtual machine on/off forcefully.

        :param vm_name: Name of the virtual machine
        :type vm_name: str
        :param action: action (poweroff, poweron)
        :type action: str
        """

    @abstractmethod
    def powerstate_vm(self, vm_name):
        """
        Returns the power state of a particular virtual machine.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        # TODO: powerstate enum

    @abstractmethod
    def restart_vm(self, vm_name, force=False):
        """
        Restarts a particular VM (default: soft reboot using guest tools).

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        :param force: Flag whether a hard reboot is requested
        :type force: bool
        """

    # Aliases
    def poweroff_vm(self, vm_name):
        """
        Turns off a particual virtual machine forcefully.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        return self._manage_power(vm_name, "poweroff")

    def poweron_vm(self, vm_name):
        """
        Turns on a particual virtual machine forcefully.

        :param vm_name: Name of a virtual machine
        :type vm_name: str
        """
        return self._manage_power(vm_name, action="poweron")
