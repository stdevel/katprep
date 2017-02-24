#!/usr/bin/env python
# -*- coding: utf-8 -*-

# katprep_snapshot.py - a script for creating a snapshot
# report of available errata and updates for systems
# managed with Foreman/Katello or Red Hat Satellite 6.
#
# 2017 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel/katprep

import argparse
import logging
import sys
import socket
import simplejson
import time
import os
from katprep_shared import get_credentials, get_api_result, get_id_by_name, validate_api_support, is_writable

vers = "0.0.1"
LOGGER = logging.getLogger('katprep-snapshot')
sat_url = ""
sat_user = ""
sat_pass = ""
system_errata = {}
output_file = ""



def parse_options(args=None):
#initialize parser
	desc='''katprep_snapshot is used for creating snapshot reports of errata available to your systems managed with Foreman/Katello or Red Hat Satellite 6. You can use two snapshot reports to create delta reports using katprep_report.py.
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
	
	#GENERIC ARGUMENTS
	#-q / --quiet
	gen_opts.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False, help="don't print status messages to stdout (default: no)")
	#-d / --debug
	gen_opts.add_argument("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs (default: no)")
	#-p / --output-path
	gen_opts.add_argument("-p", "--output-path", dest="output_path", metavar="PATH", default="", action="store", help="defines the output path for reports (default: current directory)")
	
	#SERVER ARGUMENTS
	#-a / --authfile
	srv_opts.add_argument("-a", "--authfile", dest="authfile", metavar="FILE", default="", help="defines an auth file to use instead of shell variables")
	#-s / --server
	srv_opts.add_argument("-s", "--server", dest="server", metavar="SERVER", default="localhost", help="defines the server to use (default: localhost)")
	
	#SNAPSHOT FILTER ARGUMENTS
	#-l / --location
	filter_opts_excl.add_argument("-l", "--location", action="store", default="", dest="location", metavar="NAME|ID", help="filters by a particular location (default: no)")
	#-o / --organization
	filter_opts_excl.add_argument("-o", "--organization", action="store", default="", dest="organization", metavar="NAME|ID", help="filters by an particular organization (default: no)")
	#-g / --hostgroup
	filter_opts_excl.add_argument("-g", "--hostgroup", action="store", default="", dest="hostgroup", metavar="NAME|ID", help="filters by a particular hostgroup (default: no)")
	#-e / --environment
	filter_opts_excl.add_argument("-e", "--environment", action="store", default="", dest="environment", metavar="NAME|ID", help="filters by an particular environment (default: no)")
	
	
	
	#parse options and arguments
	options = parser.parse_args()
	
	#change localhost to FQDN
	#otherwise, connections will fail
	if options.server == "localhost":
		options.server = socket.gethostname()
	
	
	return (options, args)



def scan_systems():
#scan _all_ the systems
	global sat_url, sat_user, sat_pass
	
	
	try:
		#set-up filter
		if options.location != "":
			if options.location.isdigit() == False:
				options.location = get_id_by_name(
					sat_url, sat_user, sat_pass,
					options.location, "location")
			target="/locations/{}/hosts".format(options.location)
		elif options.organization != "":
			if options.organization.isdigit() == False:
				options.organization = get_id_by_name(
					sat_url, sat_user, sat_pass,
					options.organization, "organization")
			target="/organizations/{}/hosts".format(options.organization)
		elif options.hostgroup != "":
			if options.hostgroup.isdigit() == False:
				options.hostgroup = get_id_by_name(
					sat_url, sat_user, sat_pass,
					options.hostgroup, "hostgroup")
			target="/hostgroups/{}/hosts".format(options.hostgroup)
		elif options.environment != "":
			if options.environment.isdigit() == False:
				options.hostgroup = get_id_by_name(
					sat_url, sat_user, sat_pass,
					options.environment, "environment")
			target="/environments/{}/hosts".format(options.environment)
		else:
			target="/hosts"
		LOGGER.debug("URL will be '{}{}'".format(sat_url, target))
		
		#get JSON result
		result_obj = simplejson.loads(
			get_api_result("{}{}".format(sat_url, target), sat_user, sat_pass)
		)
		
		#get errata per system
		for system in result_obj["results"]:
			LOGGER.info("Checking system '{}' (#{})...".format(system["name"], system["id"]))
			LOGGER.debug("System errata counter: security={}, bugfix={}, enhancement={}, total={}".format(
						system["content_facet_attributes"]["errata_counts"]["security"],
						system["content_facet_attributes"]["errata_counts"]["bugfix"],
						system["content_facet_attributes"]["errata_counts"]["enhancement"],
						system["content_facet_attributes"]["errata_counts"]["total"]
					))
			if int(system["content_facet_attributes"]["errata_counts"]["total"]) > 0:
				#errata applicable
				system_errata[system["name"]] = {}
				system_errata[system["name"]]["params"] = []
				system_errata[system["name"]]["errata"] = {}
				result_obj = simplejson.loads(
					get_api_result("{}/hosts/{}/errata".format(sat_url, system["id"]), sat_user, sat_pass)
				)
				#TODO: add katprep_* params here
				#system_errata[system["name"]]["params"] = ...
				system_errata[system["name"]]["errata"] = result_obj["results"]
	except KeyError as err:
		LOGGER.error("Unable to get system information, check filter options!")
	except ValueError as err:
		LOGGER.info("Unable to get data")



def create_report():
#create JSON report
	global system_errata
	
	try:
		target = open(output_file, 'w')
		target.write(
			simplejson.dumps(system_errata)
		)
		target.close()
	except IOError as err:
		LOGGER.error("Unable to store report: '{}'".format(err))
	else:
		LOGGER.info("Report '{}' created.".format(output_file))



def main(options):
#main function
	global sat_url, sat_user, sat_pass, output_file
	
	LOGGER.debug("Options: {0}".format(options))
	LOGGER.debug("Arguments: {0}".format(args))
	
	#set output file
	if options.output_path == "":
		options.output_path = "./"
	elif options.output_path != "" and options.output_path[len(options.output_path)-1:] != "/":
		#add trailing slash
		options.output_path = "{}/".format(options.output_path)
	output_file = "{}errata-snapshot-report-{}-{}.json".format(
			options.output_path,
			socket.gethostname().split('.')[0],
			time.strftime("%Y%m%d-%H%M")
			)
	LOGGER.debug("Output file will be: '{}'".format(output_file))
	
	#check if we can read and write before digging
	if is_writable(output_file):
		#initalize Satellite connection and scan systems
		(sat_user, sat_pass) = get_credentials("Satellite", options.authfile)
		sat_url = "http://{0}/api/v2".format(options.server)
		validate_api_support(sat_url, sat_user, sat_pass)
		scan_systems()
		
		#create report
		create_report()
	else:
		LOGGER.error("Directory '{}' is not writable!".format(output_file))



if __name__ == "__main__":
	(options, args) = parse_options()
	
	#set logging level
	logging.basicConfig()
	if options.debug: LOGGER.setLevel(logging.DEBUG)
	elif options.quiet: LOGGER.setLevel(logging.ERROR)
	else: LOGGER.setLevel(logging.INFO)
	
	main(options)
