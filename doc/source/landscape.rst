===============================
Represent your system landscape
===============================

In order to use katprep it is necessary to assign necessary meta information to your hosts managed by Foreman/Katello or Red Hat Satellite. katprep utilizes these information to automate maintenance tasks.

See **this site** to see a list of available host parameters and how they affect katprep.

To assign these parameters, katprep offers two utilities:

----------------
katprep_populate
----------------
``katprep_populate`` retrieves hosts and network information from your monitoring system and hypervisor. Afterwards it tries to link these information with the hosts managed by Foreman/Katello or Red Hat Satellite. In other words, it will discover which of your managed hosts are monitored and also detects virtual machines. Afterwards, these meta information are added host parameters to enable further automation.

The following example scans a vCenter Server installation (``--virt-uri``) via the pyVmomi API (``virt-type``) and an Icinga2 monitoring host (``--mon-url``). Authentication credentials are retrieved from an authentication container (``-C``). Changes are not merged into Foreman/Katello, ``katprep_populate`` only simulates what would be done (``--dry-run``)::

   $ katprep_populate --virt-uri st-vcsa03.stankowic.loc --virt-type pyvmomi --mon-url https://st-mon03.stankowic.loc:5665 -C pinkepank.auth --dry-run
   INFO:katprep_populate:This is just a SIMULATION - no changes will be made.
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt/st-vcsa03.stankowic.loc
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon_type/icinga
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_mon/https://st-mon03.stankowic.loc:5665
   INFO:katprep_populate:Host 'giertz.stankowic.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt/st-vcsa03.stankowic.loc
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_mon_type/icinga
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_mon/https://st-mon03.stankowic.loc:5665
   INFO:katprep_populate:Host 'pinkepank.test.loc' ==> set/update parameter/value: katprep_virt_type/pyvmomi

To merge the data, just omit the ``--dry-run`` parameter.

In case, monitoring and virtualization parameters for already existing hosts have changed (*e.g. new VM object name or different monitoring system*), you can easily update definitions by using the ``--update`` parameter.

------------------
katprep_parameters
------------------
``katprep_parameters`` on the other hand is used to manually bulk add/remove/modify host parameters. This can be useful if you need to edit **some** host parameters - as it is possible to filter by organization, location, hostgroup or Puppet environment. When discovering VMs with multiple IPs, ``katprep_populate`` sometimes becomes inaccurate - ``katprep_parameters`` can fix this.

The following example lists parameters relevant to katprep, than can be set with the utility::

   $ katprep_parameters --list-parameters
   INFO:katprep_parameters:Setting 'katprep_virt' will define 'Virtualization URL of the system'
   INFO:katprep_parameters:Setting 'katprep_mon' will define 'URL of the monitoring system'
   INFO:katprep_parameters:Setting 'katprep_virt_snapshot' will define 'Boolean whether system needs to be protected by a snapshot before maintenance'

The next example simply lists currently defined host parameters - authentication credentials are provided using an authentication container (``-C``)::

   $ katprep_parameters --display-parameters -C pinkepank.auth
   INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#9) --> setting 'katprep_virt' has value 'st-vcsa03.stankowic.loc' (created: 2017-03-05 10:16:38 UTC - last updated: 2017-03-05 10:23:30 UTC)
   INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#9) --> setting 'katprep_virt_type' has value 'pyvmomi' (created: 2017-03-05 10:16:38 UTC - last updated: 2017-03-05 10:23:30 UTC)
   INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#9) --> setting 'katprep_mon_type' has value 'https://st-mon03.stankowic.loc:5665' (created: 2017-03-05 10:16:38 UTC - last updated: 2017-03-05 10:23:30 UTC)
   INFO:katprep_parameters:Host 'giertz.stankowic.loc' (#9) --> setting 'katprep_mon_type' has value 'icinga' (created: 2017-03-05 10:16:38 UTC - last updated: 2017-03-05 10:23:30 UTC)
   ...

To add basic katprep-relevant parameters, use the ``--add-parameters`` parameter - to remove parameters (*e.g. after uninstalling katprep*) append ``--remove-parameters``. Values can be updated with the ``--update-parameters``  parameter::

   $ katprep_parameters --update-parameters -C pinkepank.auth
   Enter value for 'katprep_virt' (hint: Virtualization URL of the system): 
   Enter value for 'katprep_virt' (hint: Virtualization URL of the system): qemu:///system
   Enter value for 'katprep_mon' (hint: URL of the monitoring system): http://bigbrother.stankowic.loc^

It is also possible to limit actions to particular organizations (``--organization``), locations (``--location``), hostgroups (``--hosrgroup``) or Puppet environments (``--environment``).
