"""
Basic management client
"""

from abc import abstractmethod
from typing import List, Optional
from ..connector import BaseConnector


class ManagementClient(BaseConnector):
    """
    Management client class stub
    """

    @abstractmethod
    def install_pre_script(self, host):
        """
        Runs the installation pre-script
        """

    @abstractmethod
    def install_post_script(self, host):
        """
        Runs the installation post-script
        """

    @abstractmethod
    def install_plain_patches(self, host):
        """
        Installs patches without running the pre-script
        """

    @abstractmethod
    def install_plain_upgrades(self, host):
        """
        Installs upgrades without running the pre-script
        """

    def install_patches(self, host, patches: Optional[List] = None):
        """
        Apply patches on the given host.

        If no `patches` are given all patches that are available for
        the host will be installed.
        """
        if host.patch_pre_script:
            self.install_pre_script(host)
        self.install_plain_patches(host)
        if host.patch_post_script:
            self.install_post_script(host)

    @abstractmethod
    def install_upgrades(self, host, upgrades: Optional[List] = None):
        """
        Upgrade packages on the given host.
        This does include upgrades that are not part of an errata.

        If `upgrades` is `None` all upgrades on the host will be
        installed.
        """
        if host.patch_pre_script:
            self.install_pre_script(host)
        self.install_plain_upgrades(host)
        if host.patch_post_script:
            self.install_post_script(host)

    @abstractmethod
    def reboot_host(self, host):
        """
        Soft reboot of the given host.
        """
        if host.reboot_pre_script:
            self.reboot_pre_script(host)
        self.plain_reboot_host(host)
        if host.reboot_post_script:
            self.reboot_post_script(host)

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
