# -*- coding: utf-8 -*-
"""
Functions useful for work with networking.
"""

import socket


def is_ipv4(address):
    """
    Returns whether the supplied address is a valid IPv4 address

    :param address: IP address
    :type address: str
    """
    # Friendly inspired by: https://stackoverflow.com/questions/319279/
    # how-to-validate-ip-address-in-python
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count(".") == 3
    except socket.error:
        return False
    return True


def is_ipv6(address):
    """
    Returns whether the supplied address is a valid IPv6 address.

    :param address: IP address
    :type address: str
    """
    # Friendly inspired by: https://stackoverflow.com/questions/319279/
    # how-to-validate-ip-address-in-python
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:
        return False
    return True


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
