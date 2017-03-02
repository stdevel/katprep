# katprep
**katprep** is a Python toolkit for automating system maintenance and generating patch reports for systems managed with [Foreman](http://www.theforeman.org/)/[Katello](http://www.katello.org/) or [Red Hat Satellite 6.x](http://www.redhat.com/products/enterprise-linux/satellite/).
 
This can be very useful if you need to document software changes due to IT certifications like [ISO/IEC 27001:2005](http://en.wikipedia.org/wiki/ISO/IEC_27001:2005) or many other.

This toolkit is currently under early development, it's a complete rewrite of my other toolkit [**satprep**](https://github.com/stdevel/satprep), which did the same job for systems managed with [Spacewalk](http://www.spacewalkproject.org/), [Red Hat Satellite 5.x](http://www.redhat.com/products/enterprise-linux/satellite/) or [SUSE Manager](http://www.suse.com/products/suse-manager/).

So - stay tuned and check-out this site more often.

# Planned features
- Reporting
  - ~~various formats by using **Pandoc** and [**pypandoc**](https://pypi.python.org/pypi/pypandoc)~~ :white_check_mark: implemented
  - ~~creating inventory snapshots of managed systems before and after maintenance~~ :white_check_mark: implemented
  - ~~creating reports listing relevant information about installed errata (*category, date, affected packages, CVE information*)~~ :white_check_mark: implemented
  - ~~template with variables, automation using YAML metadata~~ :white_check_mark: implemented
- Automation
  - (*un-*)scheduling downtimes within popular monitoring solutions such as:
    - ~~Nagios / Icinga 1.x~~ :white_check_mark: implemented
    - Icinga 2 (*will follow soon*)
    - ~~Thruk~~ :white_check_mark: implemented
    - ~~Shinken~~ :white_check_mark: implemented
  - ~~creating/removing snapshots for virtual machines using [libvirt](http://www.libvirt.org) supporting multiple hypervisors including:~~ :white_check_mark: implemented
    - ~~KVM~~ :white_check_mark: implemented
    - ~~Xen~~ :white_check_mark: implemented
    - ~~VMware vSphere ESXi~~ :white_check_mark: implemented
    - ~~Microsoft Hyper-V~~ :white_check_mark: implemented
  - applying errata after successful preparation
  - rebooting systems if patches require this
- Documentation
  - ~~automatic Documentation with [**Sphinx**](http://www.sphinx-doc.org)~~ :white_check_mark: implemented
  - manpages for server installations without browser
  - ability to execute scripts before maintenance (*e.g. to remount ``/usr`` in rw mode*)
  - implement central configuration file to avoid using thousands of parameters
- Other
  - create a Python module for this utility
  - serve a RPM spec file for easier distribution
  - integration into Foreman user interface? :innocent:

# Planned workflow
1. Once after the installation and after new systems were registered, Puppet host parameters are set using ``katprep_parameters.py``
2. When patch maintenance is needed, a snapshot report is created using ``katprep_snapshot.py``
3. Patch maintenance per system is prepared and (*optionally*) executed using ``katprep_maintenance.py``
4. After patch maintenance, another snapshot report is created
5. Final patch reports per system are created using ``katprep_report.py``
