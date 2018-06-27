% katprep(1) Version 0.5.0 | katprep documentation

NAME
====

**katprep** — Python toolkit for automating system maintenance and generating patch reports along with Foreman/Katello and Red Hat Satellite 6.x

DESCRIPTION
===========

katprep is a toolkit for automating system maintenance tasks such as:

- Preparing system maintenance (scheduling downtimes, creating VM snapshots)
- Installing errata and non-erratum package upgrades
- Showing status of maintenance progress
- Checking monitoring and snapshot status
- Reverting VM snapshots
- Removing downtimes and snapshots
- Generating maintenance reports (e.g. because of of ISO/IEC 27001:2005 IT certifications)

For VM management, the **libvirt** and **pyVmomi** (VMware vSphere Python API bindings) libraries are used, therefore at least the following hypervisors are supported:
- VMware vSphere, Workstation, Player
- VirtualBox
- QEMU
- KVM
- XEN
- Microsoft Hyper-V

Check-out the libvirt website (https://libvirt.org/drivers.html) for additional drivers.

For managing monitoring, the following products are supported:
- Nagios/Icinga 1.x
- Icinga2

When creating reports, the document converter Pandoc is used. This enables exporting reports in various formats; this utility offers pre-defined Markdown and HTML templates.

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

Utilities
---------

The following utilities are part of the katprep framework:

- **katprep_authconfig(1)** - Manages credentials for third-party systems triggered by katprep
- **katprep_maintenance(1)** - Prepares, executes and verifies system maintenance tasks
- **katprep_parameters(1)** - Bulk edits Puppet host parameters for managed hosts
- **katprep_populate(1)** - Auto-discovers and updates monitoring and hypervisor information for managed systems
- **katprep_report(1)** - Creates reports after system maintenance
- **katprep_snapshot(1)** - Creates infrastructure status overview snapshots

Usage
-----

In order to automate system maintenance, you will need to represent your system landscape in katprep as the toolkit needs to know _which_ hosts are _VMs_ running on _which_ hypervisor monitored by _which_ monitoring system (managing physical hosts is also possible). From a Foreman perspective, these information are stored as Puppet host parameter - see also **katprep_parameters(1)**.
To omit the need of entering these information manually, two tools can assist - see **katprep_parameters(1)** and **katprep_populate(1)**.

After your infrastructure is known to katprep, it can create infrastructure status reports using **katprep_snapshot(5)**. This snapshot includes information about hosts and outstanding patches. Before and after managing hosts, a report needs to be created in order to be able to calculate the delta.
System maintenance is triggered via **katprep_maintenance(1)**. This utilities automates preparing, executing, verifying and cleaning-up maintenance tasks.

After finishing maintenance, it is possible to create maintenance reports by leveraging **katprep_report(1)**.

So, in summary - to automate patching your system landscape, execute the following tools:

1. **katprep_snapshot(1)** to create an infrastructure snapshot
2. **katprep_maintenance(1)** to prepare, execute and clean-up maintenance
3. **katprep_snapshot(1)** to create another infrastructure snapshot
4. **katprep_report(1)** to create maintenance reports (optional)

BUGS
====

See GitHub issues: <https://github.com/stdevel/katprep/issues>

AUTHOR
======

Christian Stankowic <info@cstan.io>

SEE ALSO
========

**katprep_authconfig(1)**, **katprep_maintenance(1)**, **katprep_parameters(1)**, **katprep_populate(1)**, **katprep_report(1)**, **katprep_snapshot(1)**
