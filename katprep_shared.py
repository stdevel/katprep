#!/usr/bin/env python
# -*- coding: utf-8 -*-

# katprep_shared.py - a shared library containing
# functions and calls used by other scripts of the
# katprep toolkit.
#
# 2017 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel/katprep

import getpass
import logging
import requests
import os
import stat
import simplejson

LOGGER = logging.getLogger('katprep-shared')



class APILevelNotSupportedException(Exception):
#dummy exception
	pass



def get_credentials(type, input_file=None):
#retrieve credentials
    if input_file:
        LOGGER.debug("Using authfile")
        try:
            #check filemode and read file
            filemode = oct(stat.S_IMODE(os.lstat(input_file).st_mode))
            if filemode == "0600":
                LOGGER.debug("File permission matches 0600")
                with open(input_file, "r") as auth_file:
                    s_username = auth_file.readline().replace("\n", "")
                    s_password = auth_file.readline().replace("\n", "")
                return (s_username, s_password)
            else:
                LOGGER.warning("File permissions (" + filemode + ") not matching 0600!")
        except OSError:
		LOGGER.warning("File non-existent or permissions not 0600!")
        	LOGGER.debug("Prompting for {} login credentials as we have a faulty file".format(type))
		s_username = raw_input(type + " Username: ")
		s_password = getpass.getpass(type + " Password: ")
		return (s_username, s_password)
    elif type.upper()+"_LOGIN" in os.environ and type.upper()+"_PASSWORD" in os.environ:
	#shell variables
	LOGGER.debug("Checking {} shell variables".format(type))
	return (os.environ[type.upper()+"_LOGIN"], os.environ[type.upper()+"_PASSWORD"])
    else:
	#prompt user
	LOGGER.debug("Prompting for {} login credentials".format(type))
	s_username = raw_input(type + " Username: ")
	s_password = getpass.getpass(type + " Password: ")
	return (s_username, s_password)



#TODO: def has_snapshot(virt_uri, host_username, host_password, vm_name, name):
#check whether VM has a snapshot



#TODO: def is_downtime(url, mon_username, mon_password, host, agent, no_auth=False):
#checker whether host is scheduled for downtime



#TODO: def schedule_downtime(url, mon_username, mon_password, host, hours, comment, agent="", no_auth=False, unschedule=False):
#(un)schedule downtime



#TODO: def schedule_downtime_hostgroup(url, mon_username, mon_password, hostgroup, hours, comment, agent="", no_auth=False):
#schedule downtime for hostgroup



#TODO: def get_libvirt_credentials(credentials, user_data):
#get credentials for libvirt



#TODO: def create_snapshot(virt_uri, host_username, host_password, vm_name, name, comment, remove=False):
#create/remove snapshot



#TODO: Find a nicer way to display _all_ the results...
def get_api_result(url, username, password, per_page=1337, page=1):
#send request to Foreman/Katello
	try:
		result = requests.get("{}?per_page={}&page={}".format(url, per_page, page), auth=(username, password))
		if "unable to authenticate" in result.text.lower():
			raise ValueError("Unable to authenticate")
		else: return result.text
	except ValueError as err:
		LOGGER.error(err)
		raise



def get_id_by_name(url, username, password, name, type):
#get entity ID by name
	try:
		if type.lower() not in ["hostgroup", "location", "organization", "environment"]:
			#invalid type
			raise ValueError("Unable to lookup name by invalid field type '{}'".format(type))
		else:
			#get ID by name
			result_obj = simplejson.loads(
				get_api_result("{}/{}s".format(url, type), username, password)
			)
			#TODO: nicer way than looping? numpy?
			for entry in result_obj["results"]:
				if entry["name"].lower() == name.lower():
					LOGGER.debug("{} {} seems to have ID #{}".format(type, name, entry["id"]))
					return entry["id"]
	except ValueError as err:
		LOGGER.error(err)
		pass



def validate_api_support(url, username, password):
#check whether API is supported
	try:
		#get api version
		result_obj = simplejson.loads(
			get_api_result("{}/status".format(url), username, password)
			
		)
		LOGGER.debug("API version {} found.".format(result_obj["api_version"]))
		if result_obj["api_version"] != 2:
			raise APILevelNotSupportedException(
				"Your API version ({}) does not support the required calls."
				"You'll need API version 2 - stop using historic software!".format(result_obj["api_version"])
			)
	except ValueError as err:
		LOGGER.error(err)
