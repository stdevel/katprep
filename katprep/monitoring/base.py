# -*- coding: utf-8 -*-
"""
A basic monitoring client.
"""


class MonitoringClientBase:
    def schedule_downtime(
        self, object_name, object_type, hours=8, comment="Downtime managed by katprep"
    ):
        """
        Adds scheduled downtime for a host or hostgroup.
        For this, a object name and type are required.
        Optionally, you can specify a customized comment and downtime
        period (the default is 8 hours).

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: host or hostgroup
        :type object_type: str
        :param hours: Amount of hours for the downtime (default: 8 hours)
        :type hours: int
        :param comment: Downtime comment
        :type comment: str
        """
        raise NotImplementedError("missing schedule_downtime implementation")

    def remove_downtime(self, object_name, object_type):
        """
        Removes scheduled downtime for a host or hostgroup
        For this, a object name is required.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: host or hostgroup
        :type object_type: str
        """
        raise NotImplementedError("missing remove_downtime implementation")

    def has_downtime(self, object_name, object_type="host"):
        """
        Returns whether a particular object (host, hostgroup) is currently in
        scheduled downtime. This required specifying an object name and type.

        :param object_name: Hostname or hostgroup name
        :type object_name: str
        :param object_type: Host or hostgroup (default: host)
        :type object_type: str
        """
        raise NotImplementedError("missing has_downtime implementation")

    def get_hosts(self, ipv6_only=False):
        """
        Returns hosts by their name and IP.

        :param ipv6_only: use IPv6 addresses only
        :type ipv6_only: bool
        """
        raise NotImplementedError("missing get_hosts implementation")

    def get_services(self, object_name, only_failed=True):
        """
        Returns all or failed services for a particular host.

        :param object_name:
        :type object_name: str
        :param only_failed: True will only report failed services
        :type only_failed: bool
        """
        raise NotImplementedError("missing get_services implementation")
