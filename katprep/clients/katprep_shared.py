#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some shared functions.
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
        return address.count('.') == 3
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
