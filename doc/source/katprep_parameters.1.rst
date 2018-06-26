NAME
====

**katprep\_parameters** — bulk edits Puppet host parameters for managed
hosts

SYNOPSIS
========

**katprep\_parameters** [**-h**\ ] [**-v**\ ] [**-q**\ ] [**-d**\ ]
[**-n**\ ] [**-C** *authentication\_contianer*] [**-P** *password*]
[**--insecure**\ ] [**-s** *server*] [**-l** *name*\ \|\ *id* \| **-o**
*name*\ \|\ *id* \| **-g** *name*\ \|\ *id* \| **-e** *name*\ \|\ *id*]
[**-A** \| **--add-optional-parameters** \| **-R** \| **-D** \| **-U**
\| **-L**]

DESCRIPTION
===========

Creates, removes, updates or audits Puppet host parameters used by the
katprep framework in order to automate system maintenance. Use this
utility to bulk edit host parameters, e.g. to change snapshot protection
settings per hostgroup. For the first integration of your
infrastructure, use **katprep\_populate(1)** as it offers
auto-discovery.

Host parameters
---------------

The following Puppet host parameters are created/updated:

katprep\_mon
    URL of the monitoring system (see also **Monitoring URLs**)

katprep\_mon\_name
    Object name within monitoring if ont FQDN

katprep\_mon\_type
    Monitoring system type: [*nagios*\ \|\ *icinga*] (default: icinga)

katprep\_virt
    URI of the virtualization host (see also **Virtualization URIs**)

katprep\_virt\_snapshot
    Boolean [*0*\ \|\ *1*] whether the system needs to be protected by a
    snapshot

katprep\_virt\_name
    Object name within hypervisor if not FQDN

katprep\_virt\_type
    Virtualization host type, [*libvirt*\ \|\ *pyvmovmi*] (default:
    libvirt)

Virtualization URIs
-------------------

When using **libvirt** specify a valid connection URI, such as:

| qemu+ssh://root@pinkepank.giertz.loc/system
| xen:///system
| esx:///system
| vbox:///system

See the libvirt documentation
(https://libvirt.org/guide/html/Application\_Development\_Guide-Connections-URI\_Formats.html)
for more examples.

When using **pyvmomi**, specify a valid ESXi host or vCenter Server
hostname, such as:

| vcenter.localdomain.loc
| esxi.giertz.loc

Monitoring URLs:
----------------

When using **nagios** (*NagiosCGIClient*), specify the full Nagios or
Icinga 1.x URL - make sure **not** to include **/cgi-bin**. Examples:

| https://nagios.giertz.loc/nagios
| http://omd.pinkepank.loc/icinga

When using **icinga** (*IcingaAPIClient*), specify the full API URL
including the port - such as:

https://bigbrother.giertz.loc:5665

Options
-------

-h, --help
    Prints brief usage information.

-v, --version
    Prints the current version number.

-q, --quiet
    Supresses printing status messages to stdout.

-d, --debug
    Enables debugging outputs.

-n, --dry-run
    Only simulates what would be done (default: no)

-C *filename*, --auth-container *filename*
    Defines an authentication container file (see also
    **katprep.auth(5)** and **katprep\_authconfig(1)**)

-P *passphrase*, --auth-password *passphrase*
    Defines the authentication container password to avoid password
    prompt (unattented mode)

--insecure
    Disables SSL verification (default: no)

-s *hostname*, --server *hostname*
    Defines the Foreman server to use (default: localhost)

-l *name*\ \|\ *id*, --location *name*\ \|\ *id*
    filters by particular location

-o *name*\ \|\ *id*, --organization *name*\ \|\ *id*
    filters by particular organization

-g *name*\ \|\ *id*, --hostgroup *name*\ \|\ *id*
    filters by particular hostgroup

-e *name*\ \|\ *id*, --environment *name*\ \|\ *id*
    filters by particular Puppet environment

-A, --add-parameters
    Adds built-in parameters (*katprep\_mon*, *katprep\_virt*,
    *katprep\_virt\_snapshot*) to all affected hosts (default: no)

--add-optional-parameters
    Adds optoinal built-in parameters (*katprep\_mon\_type*,
    *katprep\_mon\_name*, *katprep\_virt\_name*, *katprep\_virt\_type*)
    to all affected hosts (default: no)

-R, --remove-parameters
    Removes built-in parameters from all affected hosts (default: no)

-D, --display-parameters
    Lists values of defined parameters for affected hosts (default: no)

-U, --update-parameters
    Updates values of defined parameters for affected hosts (default:
    no)

-L, --list-parameters
    Only lists available parameters (default: no)

EXAMPLES
========

It is a good idea to start-over by specifying your monitoring and
hypervisor systems and enabling **dry-run** mode:

| $ katprep\_parameters --virt-uri st-vcsa03.stankowic.loc --virt-type
pyvmomi --mon-url https://st-mon03.stankowic.loc:5665 -C pinkepank.auth
--dry-run
| INFO:katprep\_parameters:This is just a SIMULATION - no changes will
be made.
| INFO:katprep\_parameters:Host 'giertz.stankowic.loc' ==> set/update
parameter/value: katprep\_virt/st-vcsa03.stankowic.loc
| INFO:katprep\_parameters:Host 'giertz.stankowic.loc' ==> set/update
parameter/value: katprep\_mon\_type/icinga
| ...

Check the values that would be set - run the command again with omitting
the **dry-run** parameter if they are correct.

FILES
=====

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

**katprep\_authconfig(1)**, **katprep\_populate(1)**
