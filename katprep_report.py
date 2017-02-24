#!/usr/bin/env python
# -*- coding: utf-8 -*-

# katprep_report.py - a script for creating maintenance
# reports including installed errata per system managed
# with Foreman/Katello or Red Hat Satellite 6.
#
# 2017 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel/katprep

import argparse
import logging
#import sys
#import socket
import simplejson
import time
import os
from katprep_shared import is_writable, which, is_valid_report

vers = "0.0.1"
LOGGER = logging.getLogger('katprep_report')
#sat_url = ""
#sat_user = ""
#sat_pass = ""
#system_errata = {}
output_file = ""



def parse_options(args=None):
#initialize parser
	desc='''katprep_report.py is used for creating maintenance reports including errata per system managed with Foreman/Katello or Red Hat Satellite 6.
	The utility requires two snapshots: before and after maintenance tasks were executed - just append the two files to the command line.'''
	epilog='Check-out the website for more details: http://github.com/stdevel/katprep'
	parser = argparse.ArgumentParser(description=desc, version=vers, epilog=epilog)
	
	#define option groups
	gen_opts = parser.add_argument_group("generic arguments")
	rep_opts = parser.add_argument_group("report arguments")
	
	
	#GENERIC ARGUMENTS
	#-q / --quiet
	gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False, help="don't print status messages to stdout (default: no)")
	#-d / --debug
	gen_opts.add_argument("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")
	#-p / --output-path
	gen_opts.add_argument("-p", "--output-path", dest="output_path", metavar="PATH", default="", action="store", help="defines the output path for reports (default: current directory)")
	
	#REPORT ARGUMENTS
	#-o / --output-type
	rep_opts.add_argument("-o", "--output-type", dest="output_type", metavar="FILE", default="", help="defines the output file type for Pandoc, usually this is set automatically based on the file extension (default: no)")
	#-x / --preserve-md
	rep_opts.add_argument("-x", "--preserve-md", dest="preserve_md", default=False, action="store_true", help="keeps the markdown files after creating the reports (default: no)")
	#-t / --template
	rep_opts.add_argument("-t", "--template", dest="template_file", metavar="FILE", default="", action="store", help="uses a template file (default: no)")
	#snapshot reports
	rep_opts.add_argument('reports', metavar='FILE', nargs=2, help='Two snapshot reports (before/after maintenance)', type=is_valid_report)
	
	
	
	#parse options and arguments
	options = parser.parse_args()
	
	return (options, args)



def check_pandoc():
#check Pandoc installation
	#if not which("pandoc"): return False
	if not which("vi"): return False
	return True



def create_delta():
#create delta report
	LOGGER.info("Lorem ipsum doloret...")



def create_reports():
#create JSON report
	LOGGER.info("Lorem ipsum doloret...")



def main(options):
#main function
	LOGGER.debug("Options: {0}".format(options))
	LOGGER.debug("Arguments: {0}".format(args))
	
	#set template
	if options.template_file == "":
		options.template_file = "./template.md"
	#set output file
	if options.output_path == "":
		options.output_path = "./"
	elif options.output_path != "" and options.output_path[len(options.output_path)-1:] != "/":
		#add trailing slash
		options.output_path = "{}/".format(options.output_path)
	
	#check if we can read and write before digging
	if not check_pandoc():
		LOGGER.error("Pandoc can't be found - check your installation.")
	#check if template exists
	elif not os.path.exists(options.template_file) or not os.access(options.template_file, os.R_OK):
		LOGGER.error("Template file '{}' non-existent or not readable".format(options.template_file))
	elif is_writable(options.output_path):
		#find reports
		
		#create reports
		create_reports()



if __name__ == "__main__":
	(options, args) = parse_options()
	
	#set logging level
	logging.basicConfig()
	if options.debug: LOGGER.setLevel(logging.DEBUG)
	elif options.quiet: LOGGER.setLevel(logging.ERROR)
	else: LOGGER.setLevel(logging.INFO)
	
	main(options)
