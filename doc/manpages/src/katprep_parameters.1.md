% katprep_parameters(1) Version 0.6.0 | katprep documentation

# NAME

**katprep_parameters** — Bulk edits Puppet host parameters for managed hosts

# SYNOPSIS

| **katprep_parameters** \[**-h**] \[**-v**] \[**-q**] \[**-d**] \[**-n**] \[**-C** _authentication\_contianer_] \[**-P** _password_] \[**--insecure**] \[**-s** _server_] \[**-l** _name_|_id_ | **-o** _name_|_id_ | **-g** _name_|_id_ | **-e** _name_|_id_] \[**-A** | **--add-optional-parameters** | **-R** | **-D** | **-U** | **-L**]

# DESCRIPTION

Creates, removes, updates or audits Puppet host parameters used by the **katprep(1)** framework in order to automate system maintenance.
Use this utility to bulk edit host parameters, e.g. to change snapshot protection settings per hostgroup. For the first integration of your infrastructure, use **katprep_populate(1)** as it offers auto-discovery.

## Host parameters

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

katprep_pre-script

:   Script to run before maintenance

katprep_post-script

:   Script to run after maintenance

For valid Virtualization URIs and monitoring URLs, see **katprep(1)**.

## Options

-h, --help

:   Prints brief usage information.

--version

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

# FILES

*~/.katpreprc*

:   Per-user katprep configuration file.

*katprep.auth*

:   Individual katprep authentication container file.

# BUGS

See GitHub issues: <https://github.com/stdevel/katprep/issues>

# AUTHOR

Christian Stankowic <info@cstan.io>

# SEE ALSO

**katprep(1)**, **katprep_authconfig(1)**, **katprep_populate(1)**
