"""
Host class to make working with hosts easier in the scripts.
"""

from datetime import datetime


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
    elif object_type == "erratum":
        return Erratum.from_dict(some_dict)
    else:
        raise ValueError("Unknown type {!r}".format(object_type))


class Host:

    _OBJECT_TYPE = "host"

    def __init__(
        self,
        hostname,
        host_parameters,
        organization,
        location=None,
        verifications=None,
        patches=None,
    ):
        self._hostname = hostname
        self._params = host_parameters
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
            "patches": [patch.to_dict() for patch in self._patches],
        }

        if self._location:
            host_dict["location"] = self._location

        return host_dict

    @classmethod
    def from_dict(cls, host_dict):
        try:
            # getting hostname from katello
            hostname = host_dict["params"]["name"]
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
            patches = host_dict.get("patches", [])
        patches = [Erratum.from_dict(patch) for patch in patches]

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
            self._hostname,
            self._params,
            self._organization,
            self._location,
            self._verifications,
            self._patches,
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

        if self._verifications != other._verifications:
            return False

        if self._patches != other._patches:
            return False

        return True


class Erratum:

    _OBJECT_TYPE = "erratum"

    def __init__(
        self,
        id: int,
        name: str,
        summary: str,
        issued_at: datetime,
        updated_at=None,
        reboot_suggested: bool = False,
    ):
        self.id = id
        self.name = name
        self.summary = summary
        self.issued_at = issued_at
        self.updated_at = updated_at or issued_at
        self.reboot_suggested = reboot_suggested

    def to_dict(self):
        return {
            "type": self._OBJECT_TYPE,
            "id": self.id,
            "name": self.name,
            "summary": self.summary,
            "issued_at": self.issued_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "reboot_suggested": self.reboot_suggested,
        }

    @classmethod
    def from_dict(cls, data: dict):
        if "errata_id" in data:
            return cls.from_foreman(data)
        elif "advisory_name" in data:
            return cls.from_uyuni(data)
        elif data.get("type") == cls._OBJECT_TYPE:
            def convert_to_datetime(timedata):
                if isinstance(timedata, datetime):
                    return timedata

                return datetime.fromisoformat(timedata)

            issuing_date = convert_to_datetime(data["issued_at"])
            update_date = convert_to_datetime(data["updated_at"])

            return Erratum(
                data["id"],
                data["name"],
                data["summary"],
                issuing_date,
                update_date,
                data["reboot_suggested"],
            )
        else:
            raise ValueError(f"Unable to detect parser for erratum: {data!r}")

    @classmethod
    def from_uyuni(cls, data: dict):
        def create_datetime(date_str):
            month, day, year = [int(x) for x in date_str.split("/")]

            if year <= 99:
                # We assume that we retrieved something like 21
                # which should really be 2021.
                year += 2000

            return datetime(year=year, month=month, day=day)

        issuing_date = create_datetime(data["date"])
        update_date = create_datetime(data["date"])

        # TODO: When https://github.com/uyuni-project/uyuni/issues/3733
        # is implemented make sure that we set if reboots are suggested.

        return cls(
            data["id"],
            data["advisory_name"],
            data["advisory_synopsis"],
            issuing_date,
            update_date,
        )

    @classmethod
    def from_foreman(cls, data: dict):
        def create_datetime(date_str):
            return datetime.strptime(date_str, "%Y-%m-%d")

        issuing_date = create_datetime(data["issued"])
        update_date = create_datetime(data["updated"])

        try:
            reboot = data["reboot_suggested"]
        except KeyError:
            reboot = False

        return cls(
            data["id"],
            data["errata_id"],
            data["summary"],
            issuing_date,
            update_date,
            reboot,
        )


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
