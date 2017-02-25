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
import argparse
import socket

LOGGER = logging.getLogger('katprep_shared')



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



def is_writable(path):
#checks whether the directory is writable
	if os.access(os.path.dirname(path), os.W_OK):
		return True
	else:   
		return False



def which(program):
#get path of executable if exists
	#Credits: stackoverflow.com/questions/377017/test-if-executable-exists-in-python
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	
	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None



def get_json(arg):
#return a single string of _all_ the JSON data
	try:
		with open (arg, "r") as json_file:
    			json_data=json_file.read().replace("\n", "")
		return json_data
	except Exception as err:
		LOGGER.error("Unable to read file '{}'".format(arg))



def is_valid_report(arg):
#checks whether the report is valid
	#check whether existent and readable
	if not os.path.exists(arg) or not os.access(arg, os.R_OK):
		raise argparse.ArgumentTypeError("File '{}' non-existent or not readable".format(arg))
	#check whether valid json
	try:
		json_obj = simplejson.loads(get_json(arg))
		#check whether at least one host with a params dict is found
		if "params" not in json_obj.itervalues().next().keys():
			raise argparse.ArgumentTypeError("File '{}' is not a valid JSON snapshot report.".format(arg))
	except StopIteration as err:
			raise argparse.ArgumentTypeError("File '{}' is not a valid JSON snapshot report.".format(arg))
	except ValueError as err:
		raise argparse.ArgumentTypeError("File '{}' is not a valid JSON document: '{}'".format(arg, err))






class ForemanAPIClient:
#class for accessing the Foreman API
	api_min = 2
	def __init__(self, hostname, username, password):
		#constructor, setting params
		self.hostname = self.validate_hostname(hostname)
		self.username = username
		self.password = password
		self.url = "http://{0}/api/v2".format(self.hostname)
		#check API version
		self.validate_api_support()
	
	
	
	#TODO: find a nicer way to displaying _all_ the hits...
	def get_api_result(self, sub_url, hits=1337, page=1):
		#send request
		try:
			result = requests.get("{}{}?per_page={}&page={}".format(self.url, sub_url, hits, page), auth=(self.username, self.password))
			if "unable to authenticate" in result.text.lower():
				raise ValueError("Unable to authenticate")
			else: return result.text
		except ValueError as err:
			LOGGER.error(err)
			raise
	
	
	
	def validate_api_support(self):
	#check whether API is supported
		try:
			#get api version
			result_obj = simplejson.loads(
				self.get_api_result("/status")
			)
			LOGGER.debug("API version {} found.".format(result_obj["api_version"]))
			if result_obj["api_version"] != self.api_min:
				raise APILevelNotSupportedException(
					"Your API version ({}) does not support the required calls."
					"You'll need API version {} - stop using historic software!".format(result_obj["api_version"], self.api_min)
				)
		except ValueError as err:
			LOGGER.error(err)
	
	
	
	def validate_hostname(self, hostname):
	#put the hostname in a correct format for the picky Foreman API
		if hostname == "localhost":
			#get real hostname
			hostname = socket.gethostname()
		else:
			#convert to FQDN if possible:
			fqdn = socket.gethostbyaddr(hostname)
			if "." in fqdn[0]: hostname = fqdn[0]
		return hostname
	
	
	
	def get_url(self):
	#return the configured URL
		return self.url

	def get_id_by_name(self, name, element_type):
	#get entity ID by name
		try:
			if element_type.lower() not in ["hostgroup", "location", "organization", "environment", "host"]:
				#invalid type
				raise ValueError("Unable to lookup name by invalid field type '{}'".format(element_type))
			else:
				#get ID by name
				result_obj = simplejson.loads(
					self.get_api_result("/{}s".format(element_type))
				)
				#TODO: nicer way than looping? numpy?
				for entry in result_obj["results"]:
					if entry["name"].lower() == name.lower():
						LOGGER.debug("{} {} seems to have ID #{}".format(element_type, name, entry["id"]))
						return entry["id"]
		except ValueError as err:
			LOGGER.error(err)
			pass
