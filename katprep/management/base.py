"""
Basic management client
"""

from abc import abstractmethod
from typing import List, Optional

from ..connector import BaseConnector


class ManagementClient(BaseConnector):
    @abstractmethod
    def install_patches(self, host, patches=Optional[List]):
        """
        Apply patches on the given host.

        If no `patches` are given all patches that are available for
        the host will be installed.
        """

    @abstractmethod
    def install_upgrades(self, host):
        """
        Upgrade all packages on the given host.

        This does include ugrades that are not part of an errata.
        """

    @abstractmethod
    def reboot_host(self, host):
        """
        Soft reboot of the given host.
        """

    @abstractmethod
    def is_reboot_required(self, host) -> bool:
        """
        Checks if the client requires a reboot.
        """

    @abstractmethod
    def get_errata_task_status(self, host):
        """
        Get the status of errata installations for the given host.
        """

    @abstractmethod
    def get_upgrade_task_status(self, host):
        """
        Get the status of package upgrades for the given host.
        """
