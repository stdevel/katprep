# -*- coding: utf-8 -*-
"""
Base for creating connector classes.
"""

from abc import ABCMeta, abstractmethod


class BaseConnector(metaclass=ABCMeta):
    """
    Basic management connector that connects on creation.
    """

    def __init__(self, username, password, **kwargs):
        self._username = username
        self._password = password
        self._session = None
        self._connect()

    @abstractmethod
    def _connect(self):
        pass
