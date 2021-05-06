import json
import os
import os.path
from argparse import ArgumentTypeError

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


def get_json(filename):
    """
    Reads a JSON file and returns the whole content as one-liner.

    :param filename: the JSON filename
    :type filename: str
    """
    try:
        with open(filename, "r") as json_file:
            json_data = json_file.read().replace("\n", "")
        return json_data
    except IOError as err:
        LOGGER.error("Unable to read file %r: %s", filename, err)


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


def is_valid_report(filename):
    """
    Checks whether a JSON file contains a valid snapshot report.

    :param filename: the JSON filename
    :type filename: str
    """
    if not os.path.exists(filename):
        raise ArgumentTypeError(f"File {filename!r} is non-existent")

    if not os.access(filename, os.R_OK):
        raise ArgumentTypeError(f"File {filename!r} is not readable")

    try:
        # check whether valid json
        json_obj = load_report(filename)

        if not isinstance(json_obj, dict):
            raise TypeError("The report contains the wrong root type"
                            " -  expected an object (dict).")

        if not json_obj:
            raise ValueError("The report is empty")
    except (TypeError, ValueError) as err:
        raise ArgumentTypeError(f"File {filename} is not a valid JSON"
                                f" snapshot report: {err}")
    except Exception as err:
        raise ArgumentTypeError(f"File {filename} failed to load: {err}")

    return filename
