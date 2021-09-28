"""
Basic management client
"""

from abc import abstractmethod
from typing import List

from ..connector import BaseConnector


class ManagementClient(BaseConnector):
    @abstractmethod
    def install_patches(self, host):
        """
        Apply the patches with the given errata_ids on the given host.
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
