[![Build Status](https://travis-ci.org/stdevel/katprep.svg?branch=master)](https://travis-ci.org/stdevel/katprep)
[![codecov](https://codecov.io/gh/stdevel/katprep/branch/master/graph/badge.svg)](https://codecov.io/gh/stdevel/katprep)

# katprep

**katprep** is a Python toolkit for automating system maintenance and generating patch reports for systems managed with:

- [Uyuni](https://uyuni-project.org/)
- [SUSE Manager](https://www.suse.com/products/suse-manager/)
- [Foreman](http://www.theforeman.org/) and [Katello](http://www.katello.org/)
- [Red Hat Satellite 6.x](http://www.redhat.com/products/enterprise-linux/satellite/)

This can be very useful if you need to document software changes due to IT certifications like [ISO/IEC 27001:2005](http://en.wikipedia.org/wiki/ISO/IEC_27001:2005) or many other.

katprep can automate the following infrastructure tasks:

- create/remove virtual machine snapshots hypervisor independently (*e.g. VMware vSphere, KVM, XEN, Hyper-V,...*) by utilizing [libvirt](http://www.libvirt.org) and the [VMware vSphere Python API bindings (*pyVmomi*)](https://github.com/vmware/pyvmomi)
- schedule/remove downtimes within your monitoring system (*Nagios/Icinga, Icinga2*)
- patch and reboot affected systems
- document system changes in a customizable report by utilizing [Pandoc](https://pypi.python.org/pypi/pypandoc) (*HTML, Markdown,...*)
  
This software is a complete rewrite of my other toolkit [**satprep**](https://github.com/stdevel/satprep).

## Documentation and contribution

The project documentation is created automatically using [Sphinx](http://www.sphinx-doc.org) - it can be found in the **doc** folder of this repository. Check-out [**this website**](https://stdevel.github.io/katprep/) for an online mirror.

You want to contribute? That's great! Please check-out the [**Issues**](https://github.com/stdevel/katprep/issues) tab of this project and share your thoughts/ideas in a new issue - also, pull requests are welcome!

## How does this work?

katprep uses Puppet host parameters to assign additional meta information to systems managed with Foreman/Katello or Uyuni such as:

- monitoring/virtualization system managing the host
- differing object names within those systems
- snapshots required before system maintenance

![katprep workflow](https://raw.githubusercontent.com/stdevel/katprep/master/katprep_workflow.jpg "katprep workflow")

If you plan to execute maintenance tasks, katprep triggers (*`katprep_maintenance` utility*) monitoring and virtualization hosts to schedule downtimes and create VM snapshots. Once these tasks have been completed, katprep can automatically trigger the patch installation and system reboot. After verifying your systems, katprep can remove downtimes and snapshots automatically. Before and after patching systems, it is necessary to create an inventory report of your system landscape. These reports contain information such as outstanding patches - after patching your systems, the `katprep_report` utility automatically calculares differences and creates patch reports for all updated hosts.

As a result, patching big system landscapes becomes less time-consuming with katprep: it's only executing three commands - independent whether you are patching 1 host or 1000 hosts.

To make the installation even easier, an auto-discover functionality can scan your monitoring systems and hypervisors and link gathered information with Foreman/Katello and Uyuni automatically (``katprep_populate``).
