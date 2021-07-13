# -*- coding: utf-8 -*-
"""
Base classes for virtualization managers.
"""

from abc import ABCMeta, abstractmethod


class SnapshotManager(metaclass=ABCMeta):
    """
    Managers with snapshot support.

    This base class provides a general interface for manager classes
    that support the use of snapshots.
    """

    @abstractmethod
    def _manage_snapshot(self, host, snapshot_title, snapshot_text, action="create"):
        """
        Helper function to perform creating, reverting or removing a snapshot.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Descriptive text for the snapshot
        :type snapshot_text: str
        :param action: The action to perform. create, remove or revert.
        :type action: str
        """

    @abstractmethod
    def has_snapshot(self, host, snapshot_title):
        """
        Returns whether a particular virtual machine is currently protected
        by a snapshot. This requires specifying a VM name.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """

    def create_snapshot(self, host, snapshot_title, snapshot_text):
        """
        Creates a snapshot for a particular virtual machine.
        This requires specifying a VM, comment title and text.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        :param snapshot_text: Descriptive text for the snapshot
        :type snapshot_text: str
        """
        return self._manage_snapshot(
            host, snapshot_title, snapshot_text, action="create"
        )

    def remove_snapshot(self, host, snapshot_title):
        """
        Removes a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self._manage_snapshot(host, snapshot_title, "", action="remove")

    def revert_snapshot(self, host, snapshot_title):
        """
        Reverts to  a snapshot for a particular virtual machine.
        This requires specifying a VM and a comment title.

        :param host: Host to manage
        :type host: Host
        :param snapshot_title: Snapshot title
        :type snapshot_title: str
        """
        return self._manage_snapshot(host, snapshot_title, "", action="revert")


class PowerManager(metaclass=ABCMeta):
    @abstractmethod
    def _manage_power(self, host, action="poweroff"):
        """
        Powers a particual virtual machine on/off forcefully.

        :param host: Host to manage
        :type host: Host
        :param action: action (poweroff, poweron)
        :type action: str
        """

    @abstractmethod
    def powerstate_vm(self, host):
        """
        Returns the power state of a particular virtual machine.

        :param host: Host to manage
        :type host: Host
        """
        # TODO: powerstate enum

    @abstractmethod
    def restart_vm(self, host, force=False):
        """
        Restarts a particular VM (default: soft reboot using guest tools).

        :param host: Host to manage
        :type host: Host
        :param force: Flag whether a hard reboot is requested
        :type force: bool
        """

    # Aliases
    def poweroff_vm(self, host):
        """
        Turns off a particual virtual machine forcefully.

        :param host: Host to manage
        :type host: Host
        """
        return self._manage_power(host, "poweroff")

    def poweron_vm(self, vm_name):
        """
        Turns on a particual virtual machine forcefully.

        :param host: Host to manage
        :type host: Host
        """
        return self._manage_power(host, action="poweron")
