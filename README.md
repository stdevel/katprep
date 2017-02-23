# katprep
**katprep** is a Python toolkit for automating system maintenance and generating JSON/PDF patch reports for systems managed with [Foreman](http://www.theforeman.org/)/[Katello](http://www.katello.org/) or [Red Hat Satellite 6.x](http://www.redhat.com/products/enterprise-linux/satellite/).
 
This can be very useful if you need to document software changes due to IT certifications like [ISO/IEC 27001:2005](http://en.wikipedia.org/wiki/ISO/IEC_27001:2005) or many other.

This toolkit is currently under development, it's a complete rewrite of my other toolkit [**satprep**](https://github.com/stdevel/satprep), which did the same job for systems managed with [Spacewalk](http://www.spacewalkproject.org/), [Red Hat Satellite 5.x](http://www.redhat.com/products/enterprise-linux/satellite/) or [SUSE Manager](http://www.suse.com/products/suse-manager/).

So - stay tuned and check-out this site more often.

# Planned features
- Automation
  - (*un-*)scheduling downtimes within popular monitoring solutions such as:
    - Nagios / Icinga 1.x
    - Icinga 2
    - Thruk
    - Shinken
  - creating/removing snapshots for virtual machines using [libvirt](http://www.libvirt.org) supporting multiple hypervisors including:
    - KVM
    - Xen
    - VMware vSphere ESXi
    - Microsoft Hyper-V
  - applying errata after successful preparation
  - rebooting systems if patches require this
- creating inventory snapshots of managed systems before and after maintenance
- creating reports listing relevant information about installed errata (*category, date, affected packages, CVE information*)
