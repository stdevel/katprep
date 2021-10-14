#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=not-callable
"""
A script for creating maintenance reports including installed errata per system
managed with Foreman/Katello or Red Hat Satellite 6.
"""

from __future__ import absolute_import

import argparse
import logging
import json
import datetime
import os
#import pypandoc
import yaml
from .. import __version__, is_writable, which
from ..reports import is_valid_report, load_report

"""
str: Program version
"""
LOGGER = logging.getLogger('katprep_report')
"""
logging: Logger instance
"""
LOG_LEVEL = None
"""
logging: Logger level
"""
REPORT_OLD = {}
"""
dict: Old snapshot report
"""
REPORT_NEW = {}
"""
dic: New snapshot report
"""



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''%(prog)s is used for creating maintenance reports
    including errata per system managed with Foreman/Katello or Red Hat
    Satellite 6. The utility requires two snapshots: before and after
    maintenance tasks were executed - just append the two files to the
    command line.'''
    epilog = '''Check-out the website for more details:
    http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument('--version', action='version', version=__version__)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    rep_opts = parser.add_argument_group("report arguments")

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", \
    dest="generic_quiet", default=False, help="don't print status messages " \
    "to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="generic_debug", default=False, \
    action="store_true", help="enable debugging outputs (default: no)")
    #-p / --output-path
    gen_opts.add_argument("-p", "--output-path", dest="output_path", \
    metavar="PATH", default="", action="store", \
    help="defines the output path for reports (default: current directory)")

    #REPORT ARGUMENTS
    #-o / --output-type
    rep_opts.add_argument("-o", "--output-type", dest="output_type", \
    metavar="FILE", default="", help="defines the output file type for " \
    "Pandoc, usually this is set automatically based on the template " \
    "file extension (default: no)")
    #-x / --preserve-yaml
    rep_opts.add_argument("-x", "--preserve-yaml", dest="preserve_yaml", \
    default=False, action="store_true", help="keeps the YAML metadata " \
    "after creating the reports, important for debugging (default: no)")
    #-t / --template
    rep_opts.add_argument("-t", "--template", dest="template_file", \
    metavar="FILE", default="", action="store", help="defines a dedicated" \
    " template file (default: integrated HTML)")
    #snapshot reports
    rep_opts.add_argument('reports', metavar='FILE', nargs=2, \
    help='Two snapshot reports (before/after patching)', type=is_valid_report)



    #parse options and arguments
    options = parser.parse_args()
    return (options, args)



def check_pandoc():
    """
    Checks the Pandoc installation by ensuring that the ``pandoc`` binary is
    available from the command line.
    """
    if not which("pandoc"):
        return False
    return True



def get_file_by_age(file_a, file_b, return_older=False):
    """
    Returns the newer/older file of two files. The creation time of the
    files is used as inidicator.
    There are also two alias functions available:

    :param file_a: a file
    :type file_a: str
    :param file_b: another file
    :type file_b: str
    :param return_older: returns the older file if set to True
    :type return_older: bool

.. seealso:: get_newer_file()
.. seealso:: get_older_file()
    """
    try:
        if os.path.getctime(file_a) < os.path.getctime(file_b):
            #file_b is newer
            if return_older:
                return file_a
            else:
                return file_b
        else:
            #file_a is newer
            if return_older:
                return file_b
            else:
                return file_a
    except IOError as err:
        LOGGER.error("Unable to open file: '%s'", err)

def get_newer_file(file_a, file_b):
    """
    Returns the newer of two files. The creation file of the files is used
    as indicator.

    :param file_a: a file
    :type file_a: str
    :param file_b: another file
    :type file_b: str
    """
    return get_file_by_age(file_a, file_b)

def get_older_file(file_a, file_b):
    """
    Returns the older of two files. The creation time of the files is used
    as indicator.

    :param file_a: a file
    :type file_a: str
    :param file_b: another file
    :type file_b: str
    """
    return get_file_by_age(file_a, file_b, True)



def analyze_reports(options):
    """
    Finds and loads report data. This function compares the two report files
    passed as arguments and assigns them to dedicated dictionaries (*older and
    *newer report*).
    """
    global REPORT_OLD, REPORT_NEW

    old_file = get_older_file(options.reports[0], options.reports[1])
    new_file = get_newer_file(options.reports[0], options.reports[1])

    REPORT_OLD = load_report(old_file)
    REPORT_NEW = load_report(new_file)

    LOGGER.debug(
        "Old report ist '%s', new report is '%s'", old_file, new_file
    )


def get_errata_by_host(report, hostname):
    """
    Returns all errata by a particular host in a report.

    :param report: JSON report content
    :type report: str
    :param host: hostname
    :type host: str
    """
    #TODO: find a nicer way to do this -> list comprehension?
    errata = []
    for host in report:
        if host == hostname:
            for erratum in report[host]["errata"]:
                errata.append(erratum["errata_id"])
    LOGGER.debug("Errata for host '%s': '%s'", hostname, errata)
    return errata



def create_delta(options):
    """
    Creats delta YAML reports per system. This is done by comparing the two
    snapshot reports passed as arguments.
    """
    all_hosts = set(REPORT_OLD.keys()).union(set(REPORT_NEW.keys()))
    if not all_hosts:
        raise RuntimeError("No hosts to compare.")

    newer_file = get_newer_file(options.reports[0], options.reports[1])
    file_mod_time = os.path.getmtime(newer_file)
    timestamp = datetime.datetime.fromtimestamp(file_mod_time).strftime('%Y%m%d')

    for host_id in all_hosts:
        try:
            old_host = REPORT_OLD[host_id]
        except KeyError:
            LOGGER.warn(f"Host {host_id} missing in old report")
            continue

        try:
            new_host = REPORT_NEW[host_id]
        except KeyError:
            LOGGER.warn(f"Host {host_id} missing in new report")
            continue

        if old_host.patches == new_host.patches:
            LOGGER.debug(f"Host {host_id!r} has not been patched #ohman")
            continue

        # store delta report
        filename = "{}errata-diff-{}-{}.yml".format(options.output_path, host.hostname, timestamp)
        host_json = json.dumps(old_host.to_dict())

        with open(filename, "w") as json_file:
            yaml.dump(
                yaml.load(host_json),
                json_file,
                default_flow_style=False,
                explicit_start=True,
                explicit_end=True,
                default_style="'"
            )


def create_reports(options):
    """
    Creates patch reports per system. This is done by translating the
    YAML reports created previously into the desired format using ``pandoc``.
    """
    for host in REPORT_OLD:
        timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(
            get_newer_file(options.reports[0], options.reports[1])
        )).strftime('%Y%m%d')
        filename = "{}errata-diff-{}-{}".format(
            options.output_path, host, timestamp
        )
        if os.path.isfile("{}.yml".format(filename)):
            LOGGER.debug("Creating report for host '%s'", host)
            LOGGER.debug("%s.yml", filename)
            #TODO: figure out why pypandoc doesn't work at this point
            os.system("pandoc {}.yml --template {} -o {}.{}".format(filename, \
                options.template_file, filename, options.output_type))
            if not options.preserve_yaml:
                #Remove file
                os.remove("{}.yml".format(filename))
        else:
            LOGGER.debug(
                "Non-existing report template: '%s.yml'",
                filename
            )



def main(options, args):
    """Main function, starts the logic based on parameters."""
    #set template
    if options.template_file == "":
        options.template_file = "./templates/template.html"
    if "." in options.template_file:
        #set extension as output type
        options.output_type = \
        options.template_file[options.template_file.rfind(".")+1:].lower()
    else:
        #no extension
        LOGGER.error(
            "Could not detect type of template," \
            "please add a file extension such as .md"
        )
        exit(1)

    #set output file
    if options.output_path == "":
        options.output_path = "./"
    elif options.output_path != "" and \
    options.output_path[len(options.output_path)-1:] != "/":
        #add trailing slash
        options.output_path = "{}/".format(options.output_path)

    LOGGER.debug("Options: %s", options)
    LOGGER.debug("Arguments: %s", args)

    #check if we can read and write before digging
    if not check_pandoc():
        LOGGER.error("Pandoc can't be found - check your installation.")
    #check if template exists
    elif not os.path.exists(options.template_file) or \
    not os.access(options.template_file, os.R_OK):
        LOGGER.error(
            "Template file '%s' non-existent or not readable",
            options.template_file
        )
    elif is_writable(options.output_path):
        #find reports
        analyze_reports(options)

        #create delta and reports
        create_delta(options)
        create_reports(options)


def cli():
    """
    This functions initializes the CLI interface
    """
    global LOG_LEVEL
    (options, args) = parse_options()

    #set logging level
    logging.basicConfig()
    if options.generic_debug:
        LOG_LEVEL = logging.DEBUG
    elif options.generic_quiet:
        LOG_LEVEL = logging.ERROR
    else:
        LOG_LEVEL = logging.INFO
    LOGGER.setLevel(LOG_LEVEL)

    main(options, args)



if __name__ == "__main__":
    cli()
