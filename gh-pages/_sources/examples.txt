========
Examples
========

-------------------
Simple installation
-------------------
The following example consists of:
 * an Foreman/Katello host managing hosts (``foreman.localdomain.loc``)
 * an ESXi host serving some VMs (``esxi.localdomain.loc``)
 * a Nagios server monitoring those VMs (``nagios.localdomain.loc``)
 * snapshot protection for all VMs

.. figure:: _static/example_1.png
    :alt: alternate text


Create users
============
The first step is to create appropriate service users within VMware ESXi and Nagios. These users are used to manage snapshots and downtimes. This process is described under Installation_.

.. _Installation: installation.html#api-users

Authentication
==============
The next step is to store authentication credentials in an authentication container. This is done using the ``katprep_authconfig`` utility::

   $ katprep_authconfig mycontainer.auth add
   Hostname: foreman.localdomain.loc
   foreman.localdomain.loc Username: svc-katprep
   foreman.localdomain.loc Password:
   Verify foreman.localdomain.loc Password:
   $ katprep_authconfig mycontainer.auth add
   Hostname: esxi.localdomain.loc
   esxi.localdomain.loc Username: svc-katprep
   esxi.localdomain.loc Password:
   Verify esxi.localdomain.loc Password:
   $ katprep_authconfig mycontainer.auth add
   Hostname: nagios.localdomain.loc
   nagios.localdomain.loc Username: svc-katprep
   nagios.localdomain.loc Password:
   Verify nagios.localdomain.loc Password:

To verify that required user credentials have been created, we can utilize the ``list`` sub-command::

   $ katprep_authconfig mycontainer.auth list -a
   foreman.localdomain.loc (Username: svc-katprep / Password: xxx)
   esxi.localdomain.loc (Username: svc-katprep / Password: xxx)
   nagios.localdomain.loc (Username: svc-katprep / Password: xxx)

Auto-discovery
==============
To automatically detect hosts managed by Foreman/Katello configured in Nagios and within the hypervisor, we can utilize the ``katprep_populate`` command::

   $ katprep_populate -C mycontainer.auth -s foreman.localdomain.loc --virt-uri esxi.localdomain.loc --virt-type pyvmomi --mon-url http://nagios.localdomain.loc --mon-type nagios --dry-run
   INFO:katprep_populate:This is just a SIMULATION - no changes will be made.
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt/esxi.localdomain.loc
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon_type/nagios
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon/http://nagios.localdomain.loc
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt/esxi.localdomain.loc
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_mon_type/nagios
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_mon/http://nagios.localdomain.loc
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi

Using the ``--virt-uri`` and ``--mon-url`` parameters, the ESXi and Nagios URI and URL are specified. As a Nagios system is used, the monitoring type needs to be set to ``nagios`` with the ``--mon-type`` parameter (*by default, Icinga2 is expected*). For hypervisors, the default is to utilize libvirt - as an ESXi host is used in this example, the native VMware vSphere Python bindings are enforced by setting the ``--virt-type`` parameter to ``pyvmomi``. The command above just runs a simulation to see which katprep host parameters would be set.

In this example, two hosts (``giertz.stankowic.loc`` and ``pinkepank.test.loc``) have been found on the ESXi and Nagios host. Various katprep host parameters would be set in order to enable automation. To merge this data, we just omit the ``--dry-run`` parameter and run the command again::

   $ katprep_populate -C mycontainer.auth -s foreman.localdomain.loc --virt-uri esxi.localdomain.loc --virt-type pyvmomi --mon-url http://nagios.localdomain.loc --mon-type nagios

Configuration
=============
VM snapshot flags are not set automatically using ``katprep_populate`` - we need to bulk set this flag with ``katprep_parameters``. Basically, another simulation might be a good idea. The script will ask for values for all basic katprep parameters. Entering no values will ignore changing this value. As we only want to change the ``katprep_virt_snapshot`` parameter, we will just skip all other parameters::

  $ katprep_parameters -C mycontainer.auth -s foreman.localdomain.loc -U -n
  INFO:katprep_parameters:This is just a SIMULATION - no changes will be made.
  Enter value for 'katprep_virt' (hint: Virtualization URL of the system):
  Enter value for 'katprep_mon' (hint: URL of the monitoring system):
  Enter value for 'katprep_virt_snapshot' (hint: Boolean whether system needs to be protected by a snapshot before maintenance): 1
  INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#1) --> update parameter 'katprep_virt_snapshot'
  INFO:katprep_parameters:Host 'pinkepank.test.loc' (#2) --> update parameter 'katprep_virt_snapshot'

To actually set these parameters, we just omit the ``-n`` parameter and run the command again::

  $ katprep_parameters -C mycontainer.auth -s foreman.localdomain.loc -U

System maintenance
==================
In order to automate system maintenance we need to utilize the ``katprep_snapshot`` and ``katprep_maintenance`` commands. The first step is to create a snapshot report containing information about managed hosts, available errata, hypervisor/monitoring information and so on::

  $ katprep_snapshot -C mycontainer.auth -s foreman.localdomain.loc
  INFO:katprep_snapshot:Checking system 'giertz.stankowic.loc' (#1)...
  INFO:katprep_snapshot:Checking system 'pinkepank.test.loc' (#2)...
  INFO:katprep_snapshot:Report './errata-snapshot-report-foreman-20170413-0008.json' created.

Afterwards, a JSON file is created. Know, we can prepare maintenance using the ``katprep_maintenance`` command - basically it is a good idea to use the ``--dry-run`` parameter to see what is about to happen::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomain.loc errata-snapshot-*.json --dry-run prepare
  INFO:katprep_maintenance:This is just a SIMULATION - no changes will be made.
  INFO:katprep_maintenance:Host 'giertz.stankowic.loc' --> create snapshot (katprep_20170412@giertz.stankowic.loc)
  INFO:katprep_maintenance:Host 'pinkepank.test.loc' --> create snapshot (katprep_20170412@pinkepank.test.loc)

Good - two snapshots will be created. There is no need to schedule downtimes as there is no need to reboot the systems - katprep automatically detects whether a patch requires a system reboot.

The next step is to actually prepare maintenance - so, just omit the ``--dry-run`` parameter and run the command again::

  $ katprep -C mycontainer.auth -S foreman.localdomain.loc errata-snapshot-*.json prepare

Now it's time to patch all the systems. Again, let's see what would happen::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomain.loc errata-snapshot-*.json --dry-run execute
  INFO:katprep_maintenance:This is just a SIMULATION - no changes will be made.
  INFO:katprep_maintenance:Host 'giertz.stankowic.loc' --> install: FEDORA-EPEL-2017-9d4f011d75, FEDORA-EPEL-2017-a04a2240d8
  INFO:katprep_maintenance:Host 'pinkepank.test.loc' --> install: FEDORA-EPEL-2017-9d4f011d75

Several errata will be installed on the systems. Now, go ahead and omit the simulation parameter. By default, the system will only reboot if an installed erratum requires this. If we want to automatically reboot the systems after installing errata (*regardless if an erratum requires this*), we also need to supply the ``-r`` / ``--reboot-systems`` parameter::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomain.loc errata-snapshot-*.json -r execute

Once the systems have been patched (*and maybe also rebooted*), it's time to check whether the monitoring status is fine, again::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomian.loc errata-snapshot-*.json verify

After testing the systems (*e.g. by your end-users*), the downtimes and snapshots can be cleaned up - let's simulate it, first::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomian.loc errata-snapshot-*.json -n cleanup
  INFO:katprep_maintenance:This is just a SIMULATION - no changes will be made.
  INFO:katprep_maintenance:Host 'giertz.stankowic.loc' --> remove snapshot (katprep_20170412@giertz.stankowic.loc)
  INFO:katprep_maintenance:Host 'pinkepank.test.loc' --> remove snapshot (katprep_20170412@pinkepank.test.loc)

Re-execute the command without ``-n`` to remove the snapshots::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomian.loc errata-snapshot-*.json cleanup

Verify the system status again to store the information, that we removed snapshots (*and downtimes*)::

  $ katprep_maintenance -C mycontainer.auth -S foreman.localdomian.loc errata-snapshot-*.json verify
  ERROR:PyvmomiClient:Unable to get snapshots: ''NoneType' object has no attribute 'rootSnapshotList''
  INFO:katprep_maintenance:No snapshot for host 'giertz.stankowic.loc' found, probably cleaned-up.
  ERROR:PyvmomiClient:Unable to get snapshots: ''NoneType' object has no attribute 'rootSnapshotList''
  INFO:katprep_maintenance:No snapshot for host 'pinkepank.test.loc' found, probably cleaned-up.



--------------
Advanced setup
--------------
The following example consists of:
  * an Foreman/Katello host managing hosts (``foreman.localdomain.loc``)
  * an ESXi cluster of two nodes hosting some VMs (``esxi01.localdomain.loc`` and ``esxi02.localdomain.loc``)
  * a vCenter Server installation managing the cluster (``vcenter.localdomain.loc``)
  * an Icinga2 and Nagios server monitoring those VMs (``icinga.localdomain.loc`` and ``nagios.localdomain.loc``)
  * VM and Monitoring names differing from the FQDN (e.g. ``myhost`` instead of ``myhost.localdomain.loc``)
  * snapshot protection for some VMs depending on the Puppet environment (``production`` is protected while other are not protected)

.. figure:: _static/example_2.png
    :alt: alternate text


Users are installed and auto-discovery is executed as metioned above.

Configuration
=============
The first step is to set-up the authentication container. As a vCenter Server instance is used, we don't need to enter ESXi host credentials::

   $ katprep_authconfig mycontainer.auth add -H foreman.localdomain.loc -u svc-katprep
   foreman.localdomain.loc Password:
   Verify foreman.localdomain.loc Password:
   $ katprep_authconfig mycontainer.auth add -H vcenter.localdomain.loc -u svc-katprep@vsphere.local
   vcenter.localdomain.loc Password:
   Verify vcenter.localdomain.loc Password:
   $ katprep_authconfig mycontainer.auth add -H nagios.localdomain.loc -u svc-katprep
   nagios.localdomain.loc Password:
   Verify nagios.localdomain.loc Password:
   $ katprep_authconfig mycontainer.auth add -H icinga.localdomain.loc:5665 -u svc-katprep
   icinga.localdomain.loc Password:
   Verify icinga.localdomain.loc Password:

Note that the Icinga2 host entry also contains the used API port.
The next step is to auto-discover hosts managed by Foreman/Katello configured in Nagios and within the hypervisor - simulate it, first::

  $ katprep_populate -C mycontainer.auth -s foreman.localdomain.loc --virt-uri vcenter.localdomain.loc --virt-type pyvmomi --mon-url http://nagios.localdomain.loc --mon-type nagios -n
  katprep_populate:This is just a SIMULATION - no changes will be made.
  INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt/vcenter.localdomain.loc
  INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon_type/nagios
  INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon/http://nagios.localdomain.loc
  INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi

If the result looks reasonable to you, omit the ``-n`` parameter::

  $ katprep_populate -C mycontainer.auth -s foreman.localdomain.loc --virt-uri vcenter.localdomain.loc --virt-type pyvmomi --mon-url http://nagios.localdomain.loc --mon-type nagios -n

Now, go ahead with the Icinga2 system - again, simulation is king::

  $ katprep_populate -C mycontainer.auth -s foreman.localdomain.loc --virt-uri vcenter.localdomain.loc --virt-type pyvmomi --mon-url https://icinga.localdomain.loc:5665 -n
  katprep_populate:This is just a SIMULATION - no changes will be made.
  INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt/vcenter.localdomain.loc
  INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_mon/http://icinga.localdomain.loc
  INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi

As only VMs of the ``production`` Puppet environment are protected by snapshots, the ``katprep_virt_snapshot`` setting is only set for these hosts::

  $ katprep_parameters -C mycontainer.auth -s foreman.localdomain.loc -U -e production -n
  INFO:katprep_parameters:This is just a SIMULATION - no changes will be made.
  Enter value for 'katprep_virt' (hint: Virtualization URL of the system):
  Enter value for 'katprep_mon' (hint: URL of the monitoring system):
  Enter value for 'katprep_virt_snapshot' (hint: Boolean whether system needs to be protected by a snapshot before maintenance): 1
  INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#1) --> update parameter 'katprep_virt_snapshot'

To actually change settings, omit the ``-n`` parameter::

  $ katprep_parameters -C mycontainer.auth -s foreman.localdomain.loc -U -e production

For system maintenance, refer to the previous example.
