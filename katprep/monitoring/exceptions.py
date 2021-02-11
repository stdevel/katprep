# -*- coding: utf-8 -*-
"""
Exceptions for the monitoring clients.
"""


class UnauthenticatedError(RuntimeError):
    """
    Exception for showing that a client wasn't able to authenticate itself.
    """
