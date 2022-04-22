==================
Parameter overview
==================

katprep uses multiple Puppet host parameters to control maintenance preparation and executing per system. Some parameters are created automatically using ``katprep_parameters``, some need to be created manually. The following table gives an overview:

+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| Parameter                 | Example              | Explanation                                                                           |
+===========================+======================+=======================================================================================+
| katprep_mon               | http://host/icinga   | URL of the monitoring system                                                          |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_mon_name          | giertz.stankowic.loc | Object name within monitoring if not FQDN                                             |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_mon_type          | nagios               | Monitoring host type: Nagios/Icinga 1.x (*nagios*) or Icinga2 (*icinga, default*)     |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_virt              | vpx://esx.test.loc   | Virtualization URL of the system (*libvirt or pyvmomi hostname*)                      |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_virt_name         | MYVM001              | VM name within hypervisor if not FQDN                                                 |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_virt_type         | pyvmomi              | Virtualization host type: pyvmomi (*VMware*) or libvirt (*default*)                   |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_virt_snapshot     | 1                    | Boolean (*1/0*) whether system needs to be protected by a snapshot before maintenance |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_pre-script        | /opt/stop_node.sh    | Script to run before maintenance                                                      |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_pre-script_user   | root                 | Effective pre-script user                                                             |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_pre-script_group  | root                 | Effective pre-script group                                                            |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_post-script       | /opt/start_node.sh   | Script to run after maintenance                                                       |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_post-script_user  | root                 | Effective post-script user                                                            |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
| katprep_post-script_group | root                 | Effective post-script group                                                           |
+---------------------------+----------------------+---------------------------------------------------------------------------------------+
