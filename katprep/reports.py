import json

from . import get_json
from .host import Host


def load_report(filename):
    """
    Load a report from filename.

    The returned report will be a dict containing host objects.

    :param filename: The name of the file to load from.
    :type filename: str
    :rtype: {str: Host}
    :returns: The hosts from the report
    """
    hosts = json.loads(get_json(filename))
    return {key: Host.from_dict(host) for key, host in hosts.items()}


def write_report(filename, report):
    """
    Write the given `report` to `filename`.

    :param filename: The path of the file to write to.
    :type filename: str
    :param report: The host collection to write into the file.
    :type report: dict
    """
    def convert_hosts(o):
        try:
            return o.to_dict()
        except AttributeError:
            raise TypeError(f"{o.__class__.__name__} does not support"
                            " converting to dict")

    with open(filename, "w") as target:
        target.write(json.dumps(report, default=convert_hosts))
