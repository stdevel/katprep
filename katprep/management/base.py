"""
Basic management client
"""

from abc import abstractmethod

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

    def install_patches(self, host):
        """
        Apply the patches with the given errata_ids on the given host.
        """
        if host.pre_script:
            self.install_pre_script(host)
        self.install_plain_patches(host)
        if host.post_script:
            self.install_post_script(host)

    def install_upgrades(self, host):
        """
        Upgrade all packages on the given host.

        This does include upgrades that are not part of an errata.
        """
        if host.pre_script:
            self.install_pre_script(host)
        self.install_plain_upgrades(host)
        if host.post_script:
            self.install_post_script(host)

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
