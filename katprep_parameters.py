#!/usr/bin/env python
# -*- coding: utf-8 -*-

# katprep_parameters.py - a script for managing
# Puppet host parameters for systems managed with
# Foreman/Katello or Red Hat Satellite 6.
#
# 2017 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel/katprep

import argparse
import logging
#import sys
import simplejson
#import time
#import os
from katprep_shared import get_credentials, get_api_result, validate_api_support, validate_hostname

vers = "0.0.1"
LOGGER = logging.getLogger('katprep_parameters')
sat_url = ""
sat_user = ""
sat_pass = ""
parameters = { "katprep_monitoring" : "Monitoring URL of the system ($name@URL)", "katprep_virt" : "Virtualization URL of the system ($name@URL)", "katprep_virt_snapshot" : "Boolean whether system needs to be protected by a snapshot before maintenance" }



def parse_options(args=None):
#initialize parser
	desc='''katprep_parameters.py is used for managing Puppet host parameters for systems managed with Foreman/Katello or Red Hat Satellite 6. You can create, remove and audit host parameters for all systems. These parameters are evaluated by katprep_snapshot.py to create significant reports.
	Login credentials need to be entered interactively or specified using environment variables (SATELLITE_LOGIN, SATELLITE_PASSWORD) or an authfile.
	When using an authfile, ensure that the file permissions are 0600 - otherwise the script will abort. The first line needs to contain the username, the second line represents the appropriate password.
	'''
	epilog='Check-out the website for more details: http://github.com/stdevel/katprep'
	parser = argparse.ArgumentParser(description=desc, version=vers, epilog=epilog)
	
	#define option groups
	gen_opts = parser.add_argument_group("generic arguments")
	srv_opts = parser.add_argument_group("server arguments")
	filter_opts = parser.add_argument_group("filter arguments")
	filter_opts_excl = filter_opts.add_mutually_exclusive_group()
	action_opts = parser.add_argument_group("action arguments")
	action_opts_excl = action_opts.add_mutually_exclusive_group()
	
	#GENERIC ARGUMENTS
	#-q / --quiet
	gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False, help="don't print status messages to stdout (default: no)")
	#-d / --debug
	gen_opts.add_argument("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")
	#-n / --dry-run
	gen_opts.add_argument("-n", "--dry-run", dest="dry_run", default=False, action="store_true", help="only simulate what would be done (default: no)")
	#-L / --list-parameters
	gen_opts.add_argument("-L", "--list-parameters", dest="list_only", default=False, action="store_true", help="only lists parameters this script uses (default: no)")
	
	#SERVER ARGUMENTS
	#-a / --authfile
	srv_opts.add_argument("-a", "--authfile", dest="authfile", metavar="FILE", default="", help="defines an auth file to use instead of shell variables")
	#-s / --server
	srv_opts.add_argument("-s", "--server", dest="server", metavar="SERVER", default="localhost", help="defines the server to use (default: localhost)")
	
	#FILTER ARGUMENTS
	#-l / --location
	filter_opts_excl.add_argument("-l", "--location", action="store", default="", dest="location", metavar="NAME|ID", help="filters by a particular location (default: no)")
	#-o / --organization
	filter_opts_excl.add_argument("-o", "--organization", action="store", default="", dest="organization", metavar="NAME|ID", help="filters by an particular organization (default: no)")
	#-g / --hostgroup
	filter_opts_excl.add_argument("-g", "--hostgroup", action="store", default="", dest="hostgroup", metavar="NAME|ID", help="filters by a particular hostgroup (default: no)")
	#-e / --environment
	filter_opts_excl.add_argument("-e", "--environment", action="store", default="", dest="environment", metavar="NAME|ID", help="filters by an particular environment (default: no)")
	
	#ACTION ARGUMENTS
	#-A / --add-parameters
	action_opts_excl.add_argument("-A", "--add-parameters", action="store_true", default=False, dest="action_add", help="adds built-in parameters to all affected hosts")
	#-r / --remove-parameters
	action_opts_excl.add_argument("-r", "--remove-parameters", action="store_true", default=False, dest="action_remove", help="removes built-in parameters from all affected hosts")
	#-D / --display-values
	action_opts_excl.add_argument("-D", "--display-parameters", action="store_true", default=False, dest="action_display", help="lists values of defined parameters of affected hosts")
	
	#parse options and arguments
	options = parser.parse_args()
	
	#validate hostname
	options.server = validate_hostname(options.server)
	
	return (options, args)



def main(options):
#main function
	global sat_url, sat_user, sat_pass, output_file
	
	LOGGER.debug("Options: {0}".format(options))
	LOGGER.debug("Arguments: {0}".format(args))
	
	#initalize Satellite connection
	(sat_user, sat_pass) = get_credentials("Satellite", options.authfile)
	sat_url = "http://{0}/api/v2".format(options.server)
	validate_api_support(sat_url, sat_user, sat_pass)



if __name__ == "__main__":
	(options, args) = parse_options()
	
	#set logging level
	logging.basicConfig()
	if options.debug: LOGGER.setLevel(logging.DEBUG)
	elif options.quiet: LOGGER.setLevel(logging.ERROR)
	else: LOGGER.setLevel(logging.INFO)
	
	main(options)
