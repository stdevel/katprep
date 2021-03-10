"""
Host class to make working with hosts easier in the scripts.
"""


def from_dict(some_dict):
    """
    Function for easy dict deserialisation.

    :param some_dict: The dict you want to deserialise.
    :type some_dict: dict
    """
    try:
        object_type = some_dict["type"]
    except KeyError:
        raise ValueError("Unable to get type of object from {!r}".format(some_dict))

    if object_type == "host":
        return Host.from_dict(some_dict)
    elif object_type == "hostgroup":
        return HostGroup.from_dict(some_dict)
    else:
        raise ValueError("Unknown type {!r}".format(object_type))


class Host:

    _OBJECT_TYPE = "host"

    def __init__(self, hostname, host_parameters, organisation, location=None):
        self._hostname = hostname
        self.params = host_parameters
        self._organisation = organisation
        self._location = location

    @property
    def type(self):
        return self._OBJECT_TYPE

    @property
    def hostname(self):
        return self._hostname

    @property
    def organisation(self):
        return self._organisation

    @property
    def location(self):
        if self._location is None:
            return self.organisation

        return self._location

    @property
    def virtualisation_id(self):
        try:
            virt_id = self.params["katprep_virt_name"]
        except KeyError:
            return self._hostname

        return virt_id or self._hostname

    @property
    def monitoring_id(self):
        try:
            monitoring_id = self.params["katprep_mon_name"]
        except KeyError:
            return self._hostname

        return monitoring_id or self._hostname

    def get_param(self, key):
        """
        Get the parameter from the host.

        If the `key` is unknown it will return None.

        :param key: parameter name
        :type key: str
        """
        try:
            value = self.params[key]
            if value != "":
                return value
        except KeyError:
            pass  # will return None

        return None

    def to_dict(self):
        host_dict = {
            "hostname": self._hostname,
            "params": self.params,
            "organisation": self._organisation,
            "type": self.type,
        }

        if self._location:
            host_dict["location"] = self._location

        return host_dict

    @classmethod
    def from_dict(cls, host_dict):
        return Host(
            host_dict["hostname"],
            host_dict["params"],
            host_dict["organisation"],
            host_dict.get("location"),
        )

    def __repr__(self):
        return "Host({!r}, {!r}, {!r})".format(
            self._hostname, self.params, self._organisation
        )

    def __str__(self):
        return self._hostname

    def __eq__(self, other):
        if self.hostname != other.hostname:
            return False

        if self.params != other.params:
            return False

        if self.organisation != other.organisation:
            return False

        if self.location != other.location:
            return False

        return True


class HostGroup:

    _OBJECT_TYPE = "hostgroup"

    def __init__(self, groupname):
        self._groupname = groupname

    @property
    def type(self):
        return self._OBJECT_TYPE

    @property
    def name(self):
        return self._groupname

    @property
    def monitoring_id(self):
        return self._groupname

    def to_dict(self):
        return {
            "groupname": self._groupname,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, host_dict):
        return HostGroup(host_dict["groupname"])

    def __repr__(self):
        return "HostGroup({!r})".format(self._groupname)

    def __str__(self):
        return self._groupname

    def __eq__(self, other):
        if self._groupname != other._groupname:
            return False

        return True
