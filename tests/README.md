This directory contains various tests.

# Overview
The following tests are available:

| File          | Type | Description |
|:------------- |:---- |:----------- |
| `test_ForemanAPIClient.py` | Unit test | Foreman API integration |
| `test_SpacewalkAPIClient.py` | Unit test | Spacewalk API integration |
| `test_Icinga2APIClient.py` | Unit test | Icinga 2.x API integration |
| `test_NagiosCompatibleCGIClient.py` | Unit test | Nagios/Icinga 1.x CGI integration |
| `test_PyvmomiClient.py` | Unit test | Pyvmomi integration |
| `test_LibvirtClient.py` | Unit test | Libvirt integration |

Each test has an appropriate JSON configuration file specifying connection details and objects used for the particular tests. Copy a template file (*`*.json.tmpl`*) and customize it.

## Continuous Integration
This directory also contains a [CI configuration stub](.gitlab-ci.yml) (*tested on GitLab CI*) for automating unit tests. You might be able to use this stub on other CI products such as Travis CI after altering it. Before using this configuration, have a look at it and modify it. The stub defines:
- **test** stage with multiple jobs per library
  - enable the tests you need
- jobs are executed within a Docker image **katprep-centos7** on a local registry
  - see also the [Dockerfile](tmpl-katprep-centos7/Dockerfile)

Credentials are assigned using secret variables containing the appropriate JSON content. Before running the tests, variable content is written to configuration files. Create and test JSON configuration files and paste them to your job configuration:

| Variable name | Configuration file | Description |
|:------------- |:------------------ |:----------- |
| `fman_config` | `fman_config.json` | Foreman test configuration |
| `nagios_config` | `nagios_config.json` | Nagios/Icinga 1.x test configuration |
| `icinga2_config` | `icinga2_config.json` | Icinga2 test configuration |
| `pyvmomi_config` | `pyvmomi_config.json` | Pyvmomi test configuration |
| `libvirt_config` | `libvirt_config.json` | Libvirt test configuration |
| `spw_config` | `spw_config.json` | Spacewalk test configuration |

# Tests for ForemanAPIClient
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

# Test SpacewalkAPIClient
This test checks:
- hostname verification
- valid/invalid logins
- denying legacy systems

## Preparation
For this test, you will need:
- a Spacewalk system
- a legacy Spacewalk system (*< 2.1*)
- a user per installation with read-only permissions

# Test Icinga2Client
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

# Test NagiosCompatibleCGIClient
This test checks:
- valid/invalid logins
- scheduling/removing downtimes for hosts/hostgroups
- unsupported requests (*e.g. unscheduling downtimes on Nagios systems*)
- checking downtimes
- retrieving host and service information

The tests are run for Nagios and Icinga 1.x

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

# Test PyvmomiClient
This test checks:
- valid/invalid logins
- checking/creating/reverting/removing snapshots
- retrieving VM IP information
- retrieving VM/cluster node mappings
- restarting VMs
- retrieving VM power state information
- power on/off VMs

## Preparation
For this test, you will need:
- a VMware ESXi or vCenter Server system
- an API user with permissions [as mentioned in documentation](https://stdevel.github.io/katprep/installation.html#api-users)
- a VM that can be restarted, snapshotted, etc. (**Caution: this VM is very likely to break because of numerous restarts**)

# Test LibvirtClient

This test checks:
- valid/invalid logins
- checking/creating/reverting/removing snapshots

## Preparation
For this test, you will need:
- a hypervisor supported by [libvirt](https://libvirt.org/drivers.html)
- an API user with permissions [as mentioned in documentation](https://stdevel.github.io/katprep/installation.html#api-users)
