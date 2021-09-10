"""
Basic management client
"""

from abc import abstractmethod
from typing import List

from ..connector import BaseConnector


class ManagementClient(BaseConnector):
    @abstractmethod
    def apply_patches(self, host: str, errata_ids: List):
        """
        Apply the patches with the given errata_ids on the given host.
        """

    @abstractmethod
    def upgrade_all_packages(self, host: str):
        """
        Upgrade all packages on the given host.
        """

    @abstractmethod
    def reboot_host(self, host: str):
        """
        Soft reboot of the given host.
        """
