# -*- coding: utf-8 -*-
"""
Clients to access various management systems.
"""


def get_management_client(
    management_type, log_level, username, password, hostname, *args, **kwargs
):
    """
    Factory for getting an appropriate management client.
    """
    # Use lazy importing here to not force our users to have every
    # management lib installed even though they might not use them
    if management_type == "foreman":
        from .foreman import ForemanAPIClient

        return ForemanAPIClient(
            log_level, hostname, username, password, *args, **kwargs
        )
    elif management_type == "uyuni":
        from .uyuni import UyuniAPIClient

        return UyuniAPIClient(log_level, username, password, hostname, *args, **kwargs)
    else:
        raise ValueError(f"Unknown virtualisation type {management_type!r}")


def get_virtualization_client(
    virt_type, log_level, address, username, password, *args, **kwargs
):
    """
    Factory for getting an appropriate management client.
    """
    # Use lazy importing here to not force our users to have every
    # virtualisation lib installed even though they might not use them
    if virt_type == "pyvmomi":
        from .vmware import PyvmomiClient

        return PyvmomiClient(log_level, address, username, password, *args, **kwargs)
    elif virt_type == "libvirt":
        from .libvirt import LibvirtClient

        return LibvirtClient(log_level, address, username, password, *args, **kwargs)
    else:
        raise ValueError(f"Unknown virtualisation type {virt_type!r}")
