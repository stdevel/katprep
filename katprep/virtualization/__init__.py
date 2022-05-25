# -*- coding: utf-8 -*-
"""
Clients to access various virtualization systems.
"""


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
