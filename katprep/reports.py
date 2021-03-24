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
    # TODO: Convert hosts to report hosts
    with open(filename, "w") as target:
        target.write(json.dumps(report))
