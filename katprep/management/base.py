# -*- coding: utf-8 -*-
"""
Base for creating management classes.
"""

from abc import ABCMeta, abstractmethod


class BaseConnector(metaclass=ABCMeta):

    def __init__(self, username, password, **kwargs):
        self._username = username
        self._password = password
        self._session = None
        self._connect()

    @abstractmethod
    def _connect(self):
        pass
