% katprep_populate(1) Version 0.6.0 | katprep documentation

# NAME

**katprep_populate** — Auto-discovers and updates monitoring and hypervisor information for managed systems

# SYNOPSIS

| **katprep_populate** \[**-h**] \[**--version**] \[**-q**] \[**-d**] \[**-n**] \[**-C** _authentication\_contianer_] \[**-P** _password_] \[**--ipv6-only**] \[**--insecure**] \[**--mgmt-type** _foreman_|_uyuni_] \[**-s** _server_] \[**-u**] \[**--virt-uri** _uri_] \[**--virt-type** _libvirt_|_pyvmomi_] \[**--skip-virt**] \[**--mon-url** _url_] \[**--mon-type** _nagios_|_icinga_] \[**--skip-mon**]

# DESCRIPTION

Auto-discovers monitoring host definitions and virtual machines and links those objects to Foreman hosts. This is done by comparing IP addresses and hostnames. Differing hostnames between Foreman, monitoring and hypervisor are detected and configured as host parameters (see also **Host parameters**).

To only update particular host parameters, utilize the **katprep_parameters(1)** utility.

# Host parameters

The following host parameters are created/updated:

katprep_mon

:   URL of the monitoring system (see also **Monitoring URLs**)

katprep_mon_name

:   Object name within monitoring if ont FQDN

katprep_mon_type

:   Monitoring system type: \[_nagios_|_icinga_] (default: icinga)

katprep_owner

:   System owner - REQUIRED as katprep won't manage the system otherwise

katprep_patch_post_script

:   Script to run after maintenance

katprep_patch_post_script_group

:   Effective post-script group

katprep_patch_post_script_user

:   Effective post-script user

katprep_patch_pre_script

:   Script to run before maintenance

katprep_patch_pre_script_group

:   Effective pre-script group

katprep_patch_pre_script_user

:   Effective pre-script user

katprep_reboot_post_script

:   Script to run after reboot

katprep_reboot_post_script_group

:   Effective post-script group

katprep_reboot_post_script_user

:   Effective post-script user

katprep_reboot_pre_script

:   Script to run before reboot

katprep_reboot_pre_script_group

:   Effective pre-script group

katprep_reboot_pre_script_user

:   Effective pre-script user

katprep_virt

:   URI of the virtualization host (see also **Virtualization URIs**)

katprep_virt_name

:   Object name within hypervisor if not FQDN

katprep_virt_snapshot

:   Boolean \[_0_|_1_] whether the system needs to be protected by a snapshot

katprep_virt_type

:   Virtualization host type, \[_libvirt_|_pyvmovmi_] (default: libvirt)

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

--ipv6-only

:   Filters for IPv6-only addresses (default: no)

--insecure

:   Disables SSL verification (default: no)

-s _hostname_, --server _hostname_

:   Defines the Foreman server to use (default: localhost)

-u, --update

:   Updates pre-existing host parameters (default: no)

--virt-uri _uri_

:   Defines an URI to use (see also **Virtualization URIs**)

--virt-type _libvirt_|_pyvmomi_

:   Defines the library to use for accessing the hypervisor, currently supported: _libvirt_ or _pyvmomi_ (VMware vSphere). (default: libvirt)

--skip-virt

:   Skips gathering data from hypervisor (default: no)

--mon-url _url_

:   Defines a monitoring URL to use (see also **Monitoring URLs**)

--mon-type _nagios_|_icinga_

:   Defines the monitoring sytem type, currently supported: _nagios_ (Nagios, Icinga 1.x) or _icinga_ (Icinga 2). (default: icinga)

--skip-mon

:   Skips gathering data from monitoring system (default: no)

# EXAMPLES

It is a good idea to start-over by specifying your monitoring and hypervisor systems and enabling **dry-run** mode:

| $ katprep_populate --virt-uri st-vcsa03.stankowic.loc --virt-type pyvmomi --mon-url https://st-mon03.stankowic.loc:5665 -C pinkepank.auth --dry-run
| INFO:katprep_populate:This is just a SIMULATION - no changes will be made.
| INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt/st-vcsa03.stankowic.loc
| INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon_type/icinga
| ...

Check the values that would be set - run the command again with omitting the **dry-run** parameter if they are correct.

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

**katprep(1)**, **katprep_parameters(1)**
