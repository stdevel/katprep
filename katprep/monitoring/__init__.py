# -*- coding: utf-8 -*-
"""
Interfaces for accessing monitoring systems.
"""


def get_monitoring_client(
    monitoring_type, log_level, host, username, password, *args, **kwargs
):
    """
    Factory for getting an appropriate monitoring client.
    """
    # Use lazy importing to not force our users to have every required
    # lib installed even though they might not use them
    if monitoring_type == "nagios":
        from .nagios import NagiosCGIClient

        client = NagiosCGIClient(log_level, host, username, password, *args, **kwargs)
        client.set_nagios(True)
        return client
    if monitoring_type == "icinga":
        from .nagios import NagiosCGIClient

        return NagiosCGIClient(log_level, host, username, password, *args, **kwargs)
    elif monitoring_type == "icinga2":
        from .icinga2 import Icinga2APIClient

        return Icinga2APIClient(log_level, host, username, password, *args, **kwargs)
    else:
        raise ValueError(f"Unsupported monitoring type {monitoring_type!r}")
