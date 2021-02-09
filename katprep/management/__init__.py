# -*- coding: utf-8 -*-
"""
Clients to access various management systems.
"""

import socket


def validate_hostname(hostname):
    """
    Validates using a FQDN rather than a short name as some
    APIs are very picky and SSL verification might fail.

    :param hostname: the hostname to validate
    :type hostname: str
    """
    try:
        if hostname == "localhost":
            # get real hostname
            hostname = socket.gethostname()
        if hostname.count(".") != 2:
            # get convert to FQDN if possible
            hostname = socket.getaddrinfo(
                socket.getfqdn(hostname), 0, 0, 0, 0, socket.AI_CANONNAME
            )[0][3]
    except socket.gaierror:
        raise InvalidHostnameFormatException(
            "Unable to find FQDN for host '{}'".format(hostname)
        )
    return hostname
