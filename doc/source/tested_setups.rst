=============
Tested setups
=============

katprep supports multiple Foreman, monitoring and virtualization systems. This page tries to summarize which software suites and versions have been tested. Feel free to report your experiences!

-------
Foreman
-------

+-------------------+---------+-------------+
| Product           | Version | Status/Note |
+===================+=========+=============+
| Foreman           | 1.13.x+ | working     |
+-------------------+---------+-------------+
| Red Hat Satellite | 6.2.x   | working     |
+-------------------+---------+-------------+

----------
Monitoring
----------

+---------+---------+---------------------------+
| Product | Version | Status/Note               |
+=========+=========+===========================+
| Icinga  | 1.12.x+ | working                   |
+---------+---------+---------------------------+
| Nagios  | 2.x     | untested, but should work |
+---------+---------+---------------------------+
| Nagios  | 3.x     | working                   | 
+---------+---------+---------------------------+
| Icinga2 | 2.4x    | working                   |
+---------+---------+---------------------------+

.. note::
   When using `Open Monitoring Distribution (OMD)` ensure to utilize **Basic Auth** rather than **check_mk** authorization.

--------------
Virtualization
--------------
As katprep uses libvirt for communicating with a hypervisor, all hypervisors supported by libvirt should be supported by katprep as well. On the other hand, katprep also implements **VMware vSphere SDK for Python** (*PyVmomi*) as the VMware product support by **libvirt** is poor (*e.g. libvirt does not support DRS*).

+---------------------+---------+---------------------------+
| Product             | Version | Status/Note               |
+=====================+=========+===========================+
| VMware vCenter      | 6.7     | untested, but should work |
+---------------------+---------+---------------------------+
| VMware vCenter      | 6.5     | works                     |
+---------------------+---------+---------------------------+
| VMware vCenter      | 6.0     | works                     |
+---------------------+---------+---------------------------+
| VMware vCenter      | 5.5     | untested, but should work |
+---------------------+---------+---------------------------+
| VMware vSphere ESXi | 6.7     | untested, but should work |
+---------------------+---------+---------------------------+
| VMware vSphere ESXi | 6.5     | works                     |
+---------------------+---------+---------------------------+
| VMware vSphere ESXi | 6.0     | works                     |
+---------------------+---------+---------------------------+
| VMware vSphere ESXi | 5.5     | untested, but should work |
+---------------------+---------+---------------------------+
