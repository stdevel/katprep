% katprep_parameters(1) Version 0.5.0 | katprep documentation

NAME
====

**katprep_parameters** — bulk edits Puppet host parameters for managed hosts

SYNOPSIS
========

| **katprep_parameters** \[**-h**] \[**-v**] \[**-q**] \[**-d**] \[**-n**] \[**-C** _authentication\_contianer_] \[**-P** _password_] \[**--insecure**] \[**-s** _server_] \[**-l** _name_|_id_ | **-o** _name_|_id_ | **-g** _name_|_id_ | **-e** _name_|_id_] \[**-A** | **--add-optional-parameters** | **-R** | **-D** | **-U** | **-L**]

DESCRIPTION
===========

Creates, removes, updates or audits Puppet host parameters used by the katprep framework in order to automate system maintenance.
Use this utility to bulk edit host parameters, e.g. to change snapshot protection settings per hostgroup. For the first integration of your infrastructure, use **katprep_populate(1)** as it offers auto-discovery.

Host parameters
---------------

The following Puppet host parameters are created/updated:

katprep_mon

:   URL of the monitoring system (see also **Monitoring URLs**)

katprep_mon_name

:   Object name within monitoring if ont FQDN

katprep_mon_type

:   Monitoring system type: \[_nagios_|_icinga_] (default: icinga)

katprep_virt

:   URI of the virtualization host (see also **Virtualization URIs**)

katprep_virt_snapshot

:   Boolean \[_0_|_1_] whether the system needs to be protected by a snapshot

katprep_virt_name

:   Object name within hypervisor if not FQDN

katprep_virt_type

:   Virtualization host type, \[_libvirt_|_pyvmovmi_] (default: libvirt)

Virtualization URIs
-------------------
When using **libvirt** specify a valid connection URI, such as:

| qemu+ssh://root@pinkepank.giertz.loc/system
| xen:///system
| esx:///system
| vbox:///system

See the libvirt documentation (https://libvirt.org/guide/html/Application_Development_Guide-Connections-URI_Formats.html) for more examples.

When using **pyvmomi**, specify a valid ESXi host or vCenter Server hostname, such as:

| vcenter.localdomain.loc
| esxi.giertz.loc

Monitoring URLs:
----------------
When using **nagios** (_NagiosCGIClient_), specify the full Nagios or Icinga 1.x URL - make sure **not** to include **/cgi-bin**. Examples:

| https://nagios.giertz.loc/nagios
| http://omd.pinkepank.loc/icinga

When using **icinga** (_IcingaAPIClient_), specify the full API URL including the port - such as:

| https://bigbrother.giertz.loc:5665

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

-l _name_|_id_, --location _name_|_id_

:   filters by particular location

-o _name_|_id_, --organization _name_|_id_

:   filters by particular organization

-g _name_|_id_, --hostgroup _name_|_id_

:   filters by particular hostgroup

-e _name_|_id_, --environment _name_|_id_

:   filters by particular Puppet environment

-A, --add-parameters

:   Adds built-in parameters (_katprep\_mon_, _katprep\_virt_, _katprep\_virt\_snapshot_) to all affected hosts (default: no)

--add-optional-parameters

:   Adds optoinal built-in parameters (_katprep\_mon\_type_, _katprep\_mon\_name_, _katprep\_virt\_name_, _katprep\_virt\_type_) to all affected hosts (default: no)

-R, --remove-parameters

:   Removes built-in parameters from all affected hosts (default: no)

-D, --display-parameters

:   Lists values of defined parameters for affected hosts (default: no)

-U, --update-parameters
:   Updates values of defined parameters for affected hosts (default: no)

-L, --list-parameters
:   Only lists available parameters (default: no)

EXAMPLES
========

It is a good idea to start-over by specifying your monitoring and hypervisor systems and enabling **dry-run** mode:

| $ katprep_parameters --virt-uri st-vcsa03.stankowic.loc --virt-type pyvmomi --mon-url https://st-mon03.stankowic.loc:5665 -C pinkepank.auth --dry-run
| INFO:katprep_parameters:This is just a SIMULATION - no changes will be made.
| INFO:katprep_parameters:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt/st-vcsa03.stankowic.loc
| INFO:katprep_parameters:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon_type/icinga
| ...

Check the values that would be set - run the command again with omitting the **dry-run** parameter if they are correct.

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

**katprep_authconfig(1)**, **katprep_populate(1)**
