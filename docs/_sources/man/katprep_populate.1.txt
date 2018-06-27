NAME
====

**katprep\_populate** — Auto-discovers and updates monitoring and
hypervisor information for managed systems

SYNOPSIS
========

**katprep\_populate** [**-h**\ ] [**-v**\ ] [**-q**\ ] [**-d**\ ]
[**-n**\ ] [**-C** *authentication\_contianer*] [**-P** *password*]
[**--ipv6-only**\ ] [**--insecure**\ ] [**-s** *server*] [**-u**\ ]
[**--virt-uri** *uri*] [**--virt-type** *libvirt*\ \|\ *pyvmomi*]
[**--skip-virt**\ ] [**--mon-url** *url*] [**--mon-type**
*nagios*\ \|\ *icinga*] [**--skip-mon**\ ]

DESCRIPTION
===========

Auto-discovers monitoring host definitions and virtual machines and
links those objects to Foreman hosts. This is done by comparing IP
addresses and hostnames. Differing hostnames between Foreman, monitoring
and hypervisor are detected and configured as host parameters (see also
**Host parameters**).

To only update particular host parameters, utilize the
**katprep\_parameters(1)** utility.

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

--ipv6-only
    Filters for IPv6-only addresses (default: no)

--insecure
    Disables SSL verification (default: no)

-s *hostname*, --server *hostname*
    Defines the Foreman server to use (default: localhost)

-u, --update
    Updates pre-existing host parameters (default: no)

--virt-uri *uri*
    Defines an URI to use (see also **Virtualization URIs**)

--virt-type *libvirt*\ \|\ *pyvmomi*
    Defines the library to use for accessing the hypervisor, currently
    supported: *libvirt* or *pyvmomi* (VMware vSphere). (default:
    libvirt)

--skip-virt
    Skips gathering data from hypervisor (default: no)

--mon-url *url*
    Defines a monitoring URL to use (see also **Monitoring URLs**)

--mon-type *nagios*\ \|\ *icinga*
    Defines the monitoring sytem type, currently supported: *nagios*
    (Nagios, Icinga 1.x) or *icinga* (Icinga 2). (default: icinga)

--skip-mon
    Skips gathering data from monitoring system (default: no)

EXAMPLES
========

It is a good idea to start-over by specifying your monitoring and
hypervisor systems and enabling **dry-run** mode:

| $ katprep\_populate --virt-uri st-vcsa03.stankowic.loc --virt-type
pyvmomi --mon-url https://st-mon03.stankowic.loc:5665 -C pinkepank.auth
--dry-run
| INFO:katprep\_populate:This is just a SIMULATION - no changes will be
made.
| INFO:katprep\_populate:Host 'giertz.stankowic.loc' ==> set/update
parameter/value: katprep\_virt/st-vcsa03.stankowic.loc
| INFO:katprep\_populate:Host 'giertz.stankowic.loc' ==> set/update
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

**katprep(1)**, **katprep\_parameters(1)**
