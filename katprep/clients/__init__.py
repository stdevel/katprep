#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A shared library for various exceptions and functions
of katprep client libraries
"""

import socket



class SessionException(Exception):
    """
    Dummy class for session errors

.. class:: SessionException
    """
    pass



class InvalidCredentialsException(Exception):
    """
    Dummy class for invalid credentials

.. class:: InvalidCredentialsException
    """
    pass



class APILevelNotSupportedException(Exception):
    """
    Dummy class for unsupported API levels

.. class:: APILevelNotSupportedException
    """
    pass



class UnsupportedRequestException(Exception):
    """
    Dummy class for unsupported requests

.. class:: UnsupportedRequest
    """
    pass



class InvalidHostnameFormatException(Exception):
    """
    Dummy class for invalid hostname formats (non-FQDN)

.. class:: InvalidHostnameFormatException
    """
    pass



class UnsupportedFilterException(Exception):
    """
    Dummy class for unsupported filters

.. class:: UnsupportedFilterException
    """
    pass



class EmptySetException(Exception):
    """
    Dummy class for empty result sets

.. class:: EmptySetException
    """
    pass



class SnapshotExistsException(Exception):
    """
    Dummy class for existing snapshots

.. class:: SnapshotExistsException
    """
    pass



def validate_hostname(hostname):
    """
    Validates using a FQDN rather than a short name as some
    APIs are very picky and SSL verification might fail.

    :param hostname: the hostname to validate
    :type hostname: str
    """
    try:
        if hostname == "localhost":
            #get real hostname
            hostname = socket.gethostname()
        if hostname.count('.') != 2:
            #get convert to FQDN if possible
            hostname = socket.getaddrinfo(
                socket.getfqdn(hostname), 0, 0, 0, 0,
                socket.AI_CANONNAME
            )[0][3]
    except socket.gaierror:
        raise InvalidHostnameFormatException(
            "Unable to find FQDN for host '{}'".format(hostname)
        )
    return hostname
