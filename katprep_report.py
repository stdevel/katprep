#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
katprep_report.py - a script for creating maintenance
reports including installed errata per system managed
with Foreman/Katello or Red Hat Satellite 6.

2017 By Christian Stankowic
<info at stankowic hyphen development dot net>
https://github.com/stdevel/katprep
"""

import argparse
import logging
import json
import datetime
import os
#import pypandoc
import yaml
from katprep_shared import is_writable, which, is_valid_report, get_json

__version__ = "0.0.1"
LOGGER = logging.getLogger('katprep_report')
REPORT_OLD = {}
REPORT_NEW = {}



def parse_options(args=None):
    """Parses options and arguments."""
    desc = '''katprep_report.py is used for creating maintenance reports
     including errata per system managed with Foreman/Katello or Red Hat
     Satellite 6. The utility requires two snapshots: before and after
     maintenance tasks were executed - just append the two files to the
     command line.'''
    epilog = '''Check-out the website for more details:
     http://github.com/stdevel/katprep'''
    parser = argparse.ArgumentParser(description=desc, version=__version__, \
    epilog=epilog)

    #define option groups
    gen_opts = parser.add_argument_group("generic arguments")
    rep_opts = parser.add_argument_group("report arguments")

    #GENERIC ARGUMENTS
    #-q / --quiet
    gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", \
    default=False, help="don't print status messages to stdout (default: no)")
    #-d / --debug
    gen_opts.add_argument("-d", "--debug", dest="debug", default=False, \
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
    """Checks the Pandoc installation."""
    if not which("pandoc"):
        return False
    return True



def get_newer_report(file_a, file_b, reverse=False):
    """Returns the newer/older file of two files.

    Keyword arguments:
    file_a -- a file
    file_b -- another file
    reverse -- returns the older file
    """
    try:
        if os.path.getctime(file_a) < os.path.getctime(file_b):
            #file_b is newer
            if reverse:
                return file_a
            else:
                return file_b
        else:
            #file_a is newer
            if reverse:
                return file_b
            else:
                return file_a
    except IOError as err:
        LOGGER.error("Unable to open file: '{}'".format(err))



def analyze_reports():
    """Finds and loads report data."""
    global REPORT_OLD, REPORT_NEW

    #load reports
    REPORT_OLD = json.loads(get_json(
        get_newer_report(options.reports[0], options.reports[1], True)
    ))
    REPORT_NEW = json.loads(get_json(
        get_newer_report(options.reports[0], options.reports[1])
    ))
    LOGGER.debug("Old report ist '{}', new report is '{}'".format(
        get_newer_report(options.reports[0], options.reports[1], True),
        get_newer_report(options.reports[0], options.reports[1])
        ))



def get_errata_by_host(report, hostname):
    """Returns all errata by a particular host in a report.

    Keyword arguments:
    report -- JSON report content
    host -- hostname
    """
    #TODO: find a nicer way to do this -> list comprehension?
    errata = []
    for host in report:
        if host == hostname:
            for erratum in report[host]["errata"]:
                errata.append(erratum["errata_id"])
    LOGGER.debug("Errata for host '{}': '{}'".format(hostname, errata))
    return errata



def create_delta():
    """Creats delta reports."""
    global REPORT_OLD
    #open old report and remove entries from newer report
    for host in REPORT_OLD:
        LOGGER.debug("Analyzing changes for host '{}'".format(host))
        for i, erratum in enumerate(REPORT_OLD[host]["errata"]):
            if erratum["errata_id"] in get_errata_by_host(REPORT_NEW, host):
                LOGGER.debug("Dropping erratum '{}' (#{}) as it seems not to" \
                    " be installed".format(
                        erratum["summary"], erratum["errata_id"]
                    ))
                del REPORT_OLD[host]["errata"][i]
        #store delta report
        #TODO: Integrate verify data!
        timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(
            get_newer_report(options.reports[0], options.reports[1])
        )).strftime('%Y%m%d')

        #store YAML files
        with open("{}errata-diff-{}-{}.yml".format(options.output_path, \
            host, timestamp), "w") as json_file:
            yaml.dump(yaml.load(json.dumps(REPORT_OLD[host])), json_file, \
            default_flow_style=False, explicit_start=True, \
            explicit_end=True, default_style="'")



def create_reports():
    """Creates patch reports"""
    for host in REPORT_OLD:
        LOGGER.debug("Creating report for host '{}'".format(host))
        timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(
            get_newer_report(options.reports[0], options.reports[1])
        )).strftime('%Y%m%d')
        filename = "{}errata-diff-{}-{}".format(
            options.output_path, host, timestamp
        )
        LOGGER.debug("{}.yml".format(filename))
        #TODO: figure out why pypandoc doesn't work at this point
        os.system("pandoc {}.yml --template {} -o {}.{}".format(filename, \
            options.template_file, filename, options.output_type))
        if not options.preserve_yaml:
            #Remove file
            os.remove("{}.yml".format(filename))



def main(options):
    """Main function, starts the logic based on parameters."""
    #set template
    if options.template_file == "":
        options.template_file = "./template.html"
    if options.template_file.rfind(".") != -1:
        #set extension as output type
        options.output_type = \
        options.template_file[options.template_file.rfind(".")+1:].lower()
    else:
        #no extension
        LOGGER.error("Could not detect type of template," \
        "please add a file extension such as .md")
        exit(1)

    #set output file
    if options.output_path == "":
        options.output_path = "./"
    elif options.output_path != "" and \
    options.output_path[len(options.output_path)-1:] != "/":
        #add trailing slash
        options.output_path = "{}/".format(options.output_path)

    LOGGER.debug("Options: {0}".format(options))
    LOGGER.debug("Arguments: {0}".format(args))

    #check if we can read and write before digging
    if not check_pandoc():
        LOGGER.error("Pandoc can't be found - check your installation.")
    #check if template exists
    elif not os.path.exists(options.template_file) or \
    not os.access(options.template_file, os.R_OK):
        LOGGER.error("Template file '{}' non-existent or " \
        "not readable".format(options.template_file))
    elif is_writable(options.output_path):
        #find reports
        analyze_reports()

        #create delta and reports
        create_delta()
        create_reports()



if __name__ == "__main__":
    (options, args) = parse_options()

    #set logging level
    logging.basicConfig()
    if options.debug:
        LOGGER.setLevel(logging.DEBUG)
    elif options.quiet:
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)

    main(options)
