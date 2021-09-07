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

        return UyuniAPIClient(log_level, hostname, username, password, *args, **kwargs)
    else:
        raise ValueError(f"Unknown virtualisation type {management_type!r}")
