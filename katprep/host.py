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

    def __init__(self, hostname, host_parameters, organization, location=None, verifications=None, patches=None):
        self._hostname = hostname
        self.params = host_parameters
        self._organization = organization
        self._location = location
        self._verifications = verifications or {}
        self._patches = patches or []

    @property
    def type(self):
        return self._OBJECT_TYPE

    @property
    def hostname(self):
        return self._hostname

    @property
    def organization(self):
        return self._organization

    @property
    def location(self):
        if self._location is None:
            return self.organization

        return self._location

    @property
    def virtualisation_id(self):
        try:
            virt_id = self._params["katprep_virt_name"]
        except KeyError:
            return self._hostname

        return virt_id or self._hostname

    @property
    def monitoring_id(self):
        try:
            monitoring_id = self._params["katprep_mon_name"]
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
            value = self._params[key]
            if value != "":
                return value
        except KeyError:
            pass  # will return None

        return None

    def get_verifications(self):
        """
        Return the available verifications.

        :rtype: (str, )
        """
        return tuple(self._verifications.keys())

    def get_verification(self, name):
        "Return the status of the verification of `name`."
        return self._verifications[name]

    def set_verification(self, name, value):
        "Set a verification with a given value"
        self._verifications[name] = value

    @property
    def patches(self):
        return self._patches

    def to_dict(self):
        host_dict = {
            "hostname": self._hostname,
            "params": self._params,
            "organization": self._organization,
            "type": self.type,
            "verifications": self._verifications,
            "patches": self._patches,
        }

        if self._location:
            host_dict["location"] = self._location

        return host_dict

    @classmethod
    def from_dict(cls, host_dict):
        try:
            # getting hostname from katello
            hostname = host_dict["params"]['name']
        except KeyError:
            try:
                hostname = host_dict["hostname"]
            except KeyError:
                raise ValueError(f"Unable to detect hostname of {host_dict!r}")

        try:
            # getting org from katello
            org = host_dict["params"]["organization_name"]
        except KeyError:
            org = host_dict["organization"]

        try:
            # getting org from katello
            location = host_dict["params"]["location_name"]
        except KeyError:
            location = host_dict.get("location")

        try:
            # getting patches from katello
            patches = host_dict["errata"]
        except KeyError:
            patches = host_dict.get("patches")

        return Host(
            hostname,
            host_dict["params"],
            org,
            location,
            host_dict.get("verification"),
            patches,
        )

    def __repr__(self):
        return "Host({!r}, {!r}, {!r}, {!r}, {!r}, {!r})".format(
            self._hostname, self._params, self._organization, self._location, self._verifications, self._patches
        )

    def __str__(self):
        return self._hostname

    def __eq__(self, other):
        if self.hostname != other.hostname:
            return False

        if self._params != other._params:
            return False

        if self.organization != other.organization:
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
