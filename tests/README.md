This directory contains various tests.

# Overview
The following tests are available:

| File          | Type | Description |
|:------------- |:---- |:----------- |
| `ForemanAPIClientTest.py` | Unit test | Foreman API integration |
| `SpacewalkAPIClientTest.py` | Unit test | Spacewalk API integration |
| `Icinga2APIClientTest.py` | Unit test | Icinga 2.x API integration |
| `NagiosCGIClientTest.py` | Unit test | Nagios/Icinga 1.x CGI integration |
| `PyvmomiClient.py` | Unit test | Pyvmomi integration |
| `LibvirtClient.py` | Unit test | Libvirt integration |

Each test has an appropriate JSON configuration file specifying connection details and objects used for the particular tests. Copy a template file (*`*.json.tmpl`*) and customize it.

# ForemanAPIClientTest
This test checks:
- hostname verification
- valid/invalid logins
- denying legacy systems
- `GET`/`POST`/`PUT`/`DELETE` API calls
- invalid API calls
- retrieving object names by their ID
- retrieving object IDs by their names
- retrieving host params

## Preparation
For this test, you will need:
- a Foreman installation
- a legacy Foreman installation (*APIv1*)
- a user per installation with administrative permissions
- valid objects:
  - host
  - hostgroup
  - location
  - organization
  
# SpacewalkAPIClientTest
This test checks:
- hostname verification
- valid/invalid logins
- denying legacy systems

## Preparation
For this test, you will need:
- a Spacewalk system
- a legacy Spacewalk system (*< 2.1*)
- a user per installation with read-only permissions

# Icinga2ClientTest
This test checks:
- valid/invalid logins
- scheduling/removing downtimes for hosts/hostgroups
- checking downtimes
- retrieving host and service information

## Preparation
For this test, you will need:
- an Icinga2 system
- an API user with permissions [as mentioned in documentation](https://stdevel.github.io/katprep/installation.html#api-users)
- valid objects:
  - host
  - hostgroup
  - at least one service per host

# NagiosCGIClientTest
This test checks:
- valid/invalid logins
- scheduling/removing downtimes for hosts/hostgroups
- unsupported requests (*e.g. unscheduling downtimes on Nagios systems*)
- checking downtimes
- retrieving host and service information

I highly recommend using [OMD (*Open Monitoring Distribution*)](http://omdistro.org/) as it is simple to deploy dummy sites and hosts. Make sure to use **Basic Auth** rather than check_mk authorization before running your tests.

## Preparation
For this test, you will need:
- an Icinga system
- an Nagios system
- an API user with permissions [as mentioned in documentation](https://stdevel.github.io/katprep/installation.html#api-users)
- valid objects:
  - host
  - hostgroup
  - at least one service per host

# PyvmomiClient
This test checks:
- will follow

## Preparation
For this test, you will need:
- will follow

# LibvirtClient
This test checks:
- will follow

## Preparation
For this test, you will need:
- will follow
