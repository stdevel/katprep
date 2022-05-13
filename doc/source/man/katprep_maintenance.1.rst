NAME
====

**katprep_maintenance** — Prepares, executes and verifies system
maintenance tasks

SYNOPSIS
========

| **katprep_maintenance** [**-h**] [**–version**] [**-q**] [**-d**]
  [**-n**] [**-C** *authentication_contianer*] [**-P** *password*]
  [**–insecure**] [**–mgmt-type** *foreman*\ \|\ *uyuni*] [**-s**
  *server*] [**-r**] [**-R**] [**–virt-uri** *uri*] [**-k**]
  [**–mon-url** *url*] [**–mon-type** *nagios*\ \|\ *icinga2*] [**-K**]
  [**-S**] [**-t** *hours*] [**-l** *name*\ \|\ *id* \| **-o**
  *name*\ \|\ *id* \| **-g** *name*\ \|\ *id* \| **-e**
  *name*\ \|\ *id*] [**-E** *name*] [**-I** *name*] *snapshot_report*
  [**prepare**\ \|\ **execute**\ \|\ **status**\ \|\ **revert**\ \|\ **verify**\ \|\ **cleanup**]

DESCRIPTION
===========

This utility controls maintenance tasks such as:

-  Preparing system maintenance (scheduling downtimes, creating VM
   snapshots)
-  Installing errata and non-erratum package upgrades
-  Showing status of maintenance progress
-  Checking monitoring and snapshot status
-  Reverting VM snapshots
-  Removing downtimes and snapshots

For this, host parameters for your infrastructure need to be set (see
also **katprep_populate(1)** and **katprep_parameters(1)**) and a
infrastructure snapshot needs to be available (see also
**katprep_snapshot(1)**).

If these requirements are set, all necessary information are retrieved
from Foreman - but you can also override them (e.g. force using
dedicated monitoring system).

You can filter maintenance tasks per various entities, such as
hostgroups, hostnames, locations and organizations.

Options
-------

-h, –help
   Prints brief usage information.

–version
   Prints the current version number.

-q, –quiet
   Supresses printing status messages to stdout.

-d, –debug
   Enables debugging outputs.

-n, –dry-run
   Only simulates what would be done (default: no)

-C *filename*, –auth-container *filename*
   Defines an authentication container file (see also
   **katprep.auth(5)** and **katprep_authconfig(1)**)

-P *passphrase*, –auth-password *passphrase*
   Defines the authentication container password to avoid password
   prompt (unattented mode)

–insecure
   Disables SSL verification (default: no)

-s *hostname*, –server *hostname*
   Defines the Foreman server to use (default: localhost)

-r, –reboot-systems
   Always reboot systems after successful errata installation (default:
   no, only if ``reboot_suggested`` flag set)

-R, –no-reboot
   Suppresses rebooting the system under any circumstances (default: no)
–virt-uri *uri*
   Defines an URI to use (see also **Virtualization URIs**)

-k, –skip-snapshot
   Skips gathering data from hypervisor (default: no)

–mon-url *url*
   Defines a monitoring URL to use (see also **Monitoring URLs**)

–mon-type *nagios*\ \|\ *icinga*
   Defines the monitoring sytem type, currently supported: *nagios*
   (Nagios, Icinga 1.x) or *icinga* (Icinga 2). (default: icinga)

–skip-downtime
   Skips gathering data from monitoring system (default: no)

-S, –mon-suggested
   Only schedules downtime if suggested (default: no)

-t *hours*, –mon-downtime *hours*
   Downtime period (default: 8 hours)

-l *name*\ \|\ *id*, –location *name*\ \|\ *id*
   filters by particular location

-o *name*\ \|\ *id*, –organization *name*\ \|\ *id*
   filters by particular organization

-e *name*\ \|\ *id*, –environment *name*\ \|\ *id*
   filters by particular Puppet environment

-E *hostname*, –exclude *hostname*
   Excludes particular hosts, using wildcards is possible.

-I *hostname*, –include-only *hostname*
   Only includes particular hosts (default: no)

Commands
--------

This utility supports the following commands

-  **prepare** - Preparing maintenance
-  **execute** - Installing errata and optionally package upgrades
   (**-p** / **–include-packages** parameter)
-  **status** - Display software maintenance progress (Foreman tasks)
-  **revert** - Reverting changes (currently only reverting snapshots is
   supported)
-  **verify** - Verifying status (checking snapshots and downtime)
-  **cleanup** - Cleaning-up (removing downtimes and snapshots)

**IMPORTANT NOTE**: For rebooting VMs after system maintenance, at least
Foreman 1.15.x or Red Hat Satellite 6.3 is required.

FILES
-----

*~/.katpreprc*
   Per-user katprep configuration file.

*katprep.auth*
   Individual katprep authentication container file.

BUGS
====

See GitHub issues: https://github.com/stdevel/katprep/issues

AUTHOR
======

Christian Stankowic info@cstan.io

SEE ALSO
========

**katprep(1)**, **katprep.authconfig(1)**, **katprep_parameters(1)**,
**katprep_populate(1)**, **katprep_snapshot(1)**
