#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A shared library for various exceptions of katprep client libraries
"""



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

