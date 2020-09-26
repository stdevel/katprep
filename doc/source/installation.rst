============
Requirements
============
In order to install and use katprep, the following requirements need to be met:

 * Python 2.7 or newer
 * Python modules:

  * simplejson
  * PyYAML
  * PyPandoc
  * Libvirt (*usually part of the libvirt-python package*)
  * PyVmomi (*VMware vSphere Python SDK*)

 * Pandoc (*for creating the reports*)
 * System running katprep needs access to the Foreman/Katello host using HTTPS
 * An API user for Foreman/Katello and other management systems (*Monitoring, virtualization host*)

All these Python modules are available for the most Linux distributions using the package manager or PyPi.

=========
API users
=========
To ensure that katprep is able to control hosts and retrieve data from connected management systems, create appropriate service users:

-------
Foreman
-------
Basically, katprep only needs read access to Foreman/Katello - ensure to assign the following roles to your API user:
  * Viewer
  * View hosts
  * Tasks Reader

If you want to automate create Puppet host parameters (*which can be done by using katprep_parameters and katprep_populate*) it is also necessary to assign the **Manager** role.

-------------
Nagios/Icinga
-------------
In order to schedule and remove downtimes, a service user needs to be created for katprep::

   define contact {
       contact_name                   svc-katprep
       alias                          katprep user
       use                            generic-contact
       email                          root@localhost
   }

Depending on your Nagios/Icinga configuration, it might be necessary to add the new user to the following roles in **cgi.cfg** like this::
 * authorized_for_system_information
 * authorized_for_system_commands
 * authorized_for_all_services
 * authorized_for_all_hosts
 * authorized_for_all_service_commands
 * authorized_for_all_host_commands

-------
Icinga2
-------
To enable scheduling/removing downtimes and reading host configuration from Icinga2, create an API user with the following permissions::

   #katprep user
   object ApiUser "svc-katprep" {
           password = "shittyrobots"
           permissions = [ "status/query", "objects/query/*", "actions/*" ]
   }

--------------
VMware vCenter
--------------
katprep needs to be able to read datacenter/cluster/host/vm information and create/remove snapshots. You can create a dedicated role with the following permissions:
 * Sessions

  * Validate sessions

 * Virtual machine

  * Interaction

   * Consolidate hard disks
   * Power On
   * Power Off
   * Reset

  * Snapshot management

   * Create Snapshot
   * Remove Snapshot
   * Revert Snapshot

It is a common procedure to define permissions at a global vCenter Server level.

============
Installation
============
To install katprep, you can clone the GitHub repository and install the utility or build a RPM package to install. At a later point, we might also supply pre-built RPM packages::

   $ wget https://github.com/stdevel/katprep/archive/master.zip
   $ unzip master.zip
   $ cd katprep-master

-------------------
Manual installation
-------------------
Proceed with the following steps::

   $ python setup.py install

In case you want to install the toolkit only for your current user (*e.g. because of file system restrictions*), use the **--user parameter**::

   $ python setup.py install --user

If you're a developer and want to contribute, you might prefer to install katprep in developer mode within your user context::

   $ python setup.py develop --user

---------
Build RPM
---------
Ensure to have RPM development utilities installed and proceed with the following steps::

   $ python setup.py bdist_rpm
   $ sudo yum localinstall dist/katprep*.rpm

Specifying the **--spec-only** parameter will only create a RPM spec file::

   $ python setup.py bdist_rpm --spec-only
   $ less dist/katprep.spec

