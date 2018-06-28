% katprep_maintenance(1) Version 0.5.0 | katprep documentation

NAME
====

**katprep_maintenance** — Prepares, executes and verifies system maintenance tasks

SYNOPSIS
========

| **katprep_maintenance** \[**-h**] \[**-v**] \[**-q**] \[**-d**] \[**-n**] \[**-C** _authentication\_contianer_] \[**-P** _password_] \[**--insecure**] \[**-s** _server_] \[**-r**] \[**-R**] \[**--virt-uri** _uri_] \[**-k**] \[**--mon-url** _url_] \[**--mon-type** _nagios_|_icinga_] \[**-S**] \[**-t** _hours_] \[**-l** _name_|_id_ | **-o** _name_|_id_ | **-g** _name_|_id_ | **-e** _name_|_id_] \[**-E** _name_] \[**-I** _name_] _snapshot\_report_ \[**prepare**|**execute**|**status**|**revert**|**verify**|**cleanup**]

DESCRIPTION
===========

This utility controls maintenance tasks such as:

- Preparing system maintenance (scheduling downtimes, creating VM snapshots)
- Installing errata and non-erratum package upgrades
- Showing status of maintenance progress
- Checking monitoring and snapshot status
- Reverting VM snapshots
- Removing downtimes and snapshots

For this, host parameters for your infrastructure need to be set (see also **katprep_populate(1)** and **katprep_parameters(1)**) and a infrastructure snapshot needs to be available (see also **katprep_snapshot(1)**).

If these requirements are set, all necessary information are retrieved from Foreman - but you can also override them (e.g. force using dedicated monitoring system).

You can filter maintenance tasks per various entities, such as hostgroups, hostnames, locations and organizations.

Options
-------

-h, --help

:   Prints brief usage information.

-v, --version

:   Prints the current version number.

-q, --quiet

:   Supresses printing status messages to stdout.

-d, --debug

:   Enables debugging outputs.

-n, --dry-run

:   Only simulates what would be done (default: no)

-C _filename_, --auth-container _filename_

:   Defines an authentication container file (see also **katprep.auth(5)** and **katprep_authconfig(1)**)

-P _passphrase_, --auth-password _passphrase_

:   Defines the authentication container password to avoid password prompt (unattented mode)

--insecure

:   Disables SSL verification (default: no)

-s _hostname_, --server _hostname_

:   Defines the Foreman server to use (default: localhost)

-r, --reboot-systems

:   Always reboot systems after successful errata installation (default: no, only if `reboot_suggested` flag set)

-R, --no-reboot
:   Suppresses rebooting the system under any circumstances (default: no)

--virt-uri _uri_

:   Defines an URI to use (see also **Virtualization URIs**)

-k, --skip-snapshot

:   Skips gathering data from hypervisor (default: no)

--mon-url _url_

:   Defines a monitoring URL to use (see also **Monitoring URLs**)

--mon-type _nagios_|_icinga_

:   Defines the monitoring sytem type, currently supported: _nagios_ (Nagios, Icinga 1.x) or _icinga_ (Icinga 2). (default: icinga)

--skip-downtime

:   Skips gathering data from monitoring system (default: no)

-S, --mon-suggested

:   Only schedules downtime if suggested (default: no)

-t _hours_, --mon-downtime _hours_

:   Downtime period (default: 8 hours)

-l _name_|_id_, --location _name_|_id_

:   filters by particular location

-o _name_|_id_, --organization _name_|_id_

:   filters by particular organization

-e _name_|_id_, --environment _name_|_id_

:   filters by particular Puppet environment

-E _hostname_, --exclude _hostname_

:   Excludes particular hosts, using wildcards is possible.

-I _hostname_, --include-only _hostname_

:   Only includes particular hosts (default: no)

Commands
--------

This utility supports the following commands

- **prepare** - Preparing maintenance
- **execute** - Installing errata and optionally package upgrades (**-p** / **--include-packages** parameter)
- **status** - Display software maintenance progress (Foreman tasks)
- **revert** - Reverting changes (currently only reverting snapshots is supported)
- **verify** - Verifying status (checking snapshots and downtime)
- **cleanup** - Cleaning-up (removing downtimes and snapshots)

FILES
=====

*~/.katpreprc*

:   Per-user katprep configuration file.

*katprep.auth*

:   Individual katprep authentication container file.

BUGS
====

See GitHub issues: <https://github.com/stdevel/katprep/issues>

AUTHOR
======

Christian Stankowic <info@cstan.io>

SEE ALSO
========

**katprep(1)**, **katprep.authconfig(1)**, **katprep_parameters(1)**, **katprep_populate(1)**, **katprep_snapshot(1)**
