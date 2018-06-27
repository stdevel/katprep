NAME
====

**katprep\_parameters** — Bulk edits Puppet host parameters for managed
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
**katprep(1)** framework in order to automate system maintenance. Use
this utility to bulk edit host parameters, e.g. to change snapshot
protection settings per hostgroup. For the first integration of your
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

For valid Virtualization URIs and monitoring URLs, see **katprep(1)**.

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

**katprep(1)**, **katprep\_authconfig(1)**, **katprep\_populate(1)**
