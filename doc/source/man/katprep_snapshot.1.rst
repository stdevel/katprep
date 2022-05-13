NAME
====

**katprep_snapshot** — Creates infrastructure status overview snapshots

SYNOPSIS
========

| **katprep_snapshot** [**-h**] [**--version**] [**-q**] [**-d**] [**-p**
  *path*] [**-C** *authentication_contianer*] [**-P** *password*]
  [--mgmt-type foreman|uyuni] [**-s** *server*] [**--insecure**]
  [**-l** *name*\ \|\ *id* \| **-o** 
  *name*\ \|\ *id* \| **-g** *name*\ \|\ *id* \| **-e**
  *name*\ \|\ *id*]
  [**-E** *name*]

DESCRIPTION
===========

Creates infrastructure status overview snapshots including host
information such as:

-  system information (IP address, operating system, owner,…)
-  katprep configuration parameters (monitoring and hypervisor
   configuration)
-  errata information (outstanding patches)

These information are required by the **katprep(1)** framework in order
to create maintenance reports using **katprep_report(1)**.

Run this utility before and after maintaining systems using
**katprep_maintenance(1)**.

Options
-------

-h, --help
   Prints brief usage information.

--version
   Prints the current version number.

-q, --quiet
   Supresses printing status messages to stdout.

-d, --debug
   Enables debugging outputs.

-p *path*, --output-path *path*
   Defines the report output path (default: current directory)

-C *filename*, --auth-container *filename*
   Defines an authentication container file (see also
   **katprep.auth(5)** and **katprep_authconfig(1)**)

-P *passphrase*, --auth-password *passphrase*
   Defines the authentication container password to avoid password
   prompt (unattented mode)

--mgmt-type
   defines the library used to operate with management host:
   foreman or uyuni (default: foreman)

-s *hostname*, --server *hostname*
   Defines the Foreman server to use (default: localhost)

--insecure
   Disables SSL verification (default: no)

-E *hostname*, --exclude *hostname*
   Excludes particular hosts, using wildcards is possible.

-l *name*\ \|\ *id*, --location *name*\ \|\ *id*
   filters by particular location

-o *name*\ \|\ *id*, --organization *name*\ \|\ *id*
   filters by particular organization

-g *name*\ \|\ *id*, --hostgroup *name*\ \|\ *id*
   filters by particular hostgroup

-e *name*\ \|\ *id*, --environment *name*\ \|\ *id*
   filters by particular Puppet environment

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

**katprep(1)**, **katprep_maintenance(1)**, **katprep_report(1)**
