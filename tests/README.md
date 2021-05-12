# Overview

This directory contains various tests:

| File          | Type | Description |
|:------------- |:---- |:----------- |
| `test_ForemanAPIClient.py` | Unit test | Foreman API integration |
| `test_UyuniAPIClient.py` | Unit test | Uyuni API integration |
| `test_Icinga2APIClient.py` | Unit test | Icinga 2.x API integration |
| `test_NagiosCompatibleCGIClient.py` | Unit test | Nagios CGI integration |
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
| `uyuni_config` | `uyuni_config.json` | Uyuni test configuration |

## Running tests using Vagrantboxes

This directory contains a [`Vagrantfile`](Vagrantfile) for creating your own testing environment. Simply start it using:

```shell
$ vagrant up
```

After having the machines up and running you can link your tests again the Vagrant test configurations:

```shell
$ ln -s icinga2_config.json.vagrant icinga2_config.json
$ ln -s nagios_config.json.vagrant nagios_config.json
$ ln -s uyuni_config.json.vagrant uyuni_config.json
```

Now you can run `pytest` against the APIs running in VMs - e.g.:

```shell
$ pytest test_UyuniAPICLient.py
```

## See also

- [Testing older Uyuni releases](Uyuni.md)
