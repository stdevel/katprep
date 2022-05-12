% katprep_snapshot(1) Version 0.5.0 | katprep documentation

# NAME

**katprep_snapshot** — Creates infrastructure status overview snapshots

# SYNOPSIS

| **katprep_snapshot** \[**-h**] \[**-v**] \[**-q**] \[**-d**] \[**-p** _path_] \[**-C** _authentication\_contianer_] \[**-P** _password_] \[**-s** _server_] \[**--insecure**] \[**-l** _name_|_id_ | **-o** _name_|_id_ | **-g** _name_|_id_ | **-e** _name_|_id_] \[**-E** _name_]

# DESCRIPTION

Creates infrastructure status overview snapshots including host information such as:

- system information (IP address, operating system, owner,...)
- katprep configuration parameters (monitoring and hypervisor configuration)
- errata information (outstanding patches)

These information are required by the **katprep(1)** framework in order to create maintenance reports using **katprep_report(1)**.

Run this utility before and after maintaining systems using **katprep_maintenance(1)**.

## Options

-h, --help

:   Prints brief usage information.

-v, --version

:   Prints the current version number.

-q, --quiet

:   Supresses printing status messages to stdout.

-d, --debug

:   Enables debugging outputs.

-p _path_, --output-path _path_

:   Defines the report output path (default: current directory)

-C _filename_, --auth-container _filename_

:   Defines an authentication container file (see also **katprep.auth(5)** and **katprep_authconfig(1)**)

-P _passphrase_, --auth-password _passphrase_

:   Defines the authentication container password to avoid password prompt (unattented mode)

-s _hostname_, --server _hostname_

:   Defines the Foreman server to use (default: localhost)

--insecure

:   Disables SSL verification (default: no)

-E _hostname_, --exclude _hostname_

:   Excludes particular hosts, using wildcards is possible.

-l _name_|_id_, --location _name_|_id_

:   filters by particular location

-o _name_|_id_, --organization _name_|_id_

:   filters by particular organization

-g _name_|_id_, --hostgroup _name_|_id_

:   filters by particular hostgroup

-e _name_|_id_, --environment _name_|_id_

:   filters by particular Puppet environment

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

**katprep(1)**, **katprep_maintenance(1)**, **katprep_report(1)**
