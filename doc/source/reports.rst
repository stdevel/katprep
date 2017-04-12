===========
Customizing
===========

The ``katprep_report`` utility uses **Pandoc** and special templates in order to automate creating patch reports per host. Default templates are part of every katprep installation - it is also possible to alter these templates to match your company needs (*e.g. corporate identity*).

To start over, check-out the ``templates`` directory as it contains the basic templates.

It is basically a good idea to assign the file extension that represents the report file type to your template - e.g. ``.html`` for HTML pages, ``.pdf`` for PDF documents, etc. Otherwise ``katprep_report`` might not auto-discover the appropriate Pandoc type. In this case you need to specify the ``-o`` / ``--output-type`` parameter::

  $ katprep_report *.json -t templates/my_strange.tmp -o html

---------
Variables
---------
When creating host reports, a temporary YAML file is created per host. This file contains all the variables that are rendered into a host report using Pandoc. Use ``katprep_report`` along with the ``-x`` / ``--preserve-yaml`` parameter to keep this file. Refer to that file to explore available variables.

The following tables list commonly used variables:

Errata information
==================

+-------------------------------+-------------------------------------------+
| Parameter                     | Explanation                               |
+===============================+===========================================+
| errata.cves                   | Common Vulnerability and Exposure names   |
+-------------------------------+-------------------------------------------+
| errata.description            | Erratum description                       |
+-------------------------------+-------------------------------------------+
| errata.errata_id              | Erratum ID (*packager naming convention*) |
+-------------------------------+-------------------------------------------+
| errata.hosts_applicable_count | Number of hosts erratum is applicable to  |
+-------------------------------+-------------------------------------------+
| errata.hosts_available_count  | Number of hosts erratum is available to   |
+-------------------------------+-------------------------------------------+
| errata.id                     | Katello erratum ID                        |
+-------------------------------+-------------------------------------------+
| errata.installable            | Flag whether installable on this host     |
+-------------------------------+-------------------------------------------+
| errata.issued                 | Erratum release date                      |
+-------------------------------+-------------------------------------------+
| errata.packages               | Package names relevant to this erratum    |
+-------------------------------+-------------------------------------------+
| errata.reboot_suggested       | Flag whether reboot is suggested          |
+-------------------------------+-------------------------------------------+
| errata.severity               | Erratum severity                          |
+-------------------------------+-------------------------------------------+
| errata.solution               | Erratum solution description/link         |
+-------------------------------+-------------------------------------------+
| errata.summary                | Erratum short summary                     |
+-------------------------------+-------------------------------------------+
| errata.title                  | Erratum title                             |
+-------------------------------+-------------------------------------------+
| errata.type                   | Erratum type (*enhancement, bugfix,...*)  |
+-------------------------------+-------------------------------------------+

These parameters apply to an particular erratum that is handled within Pandoc in a for-loop - e.g. in the HTML template::

  $for(errata)$
  <tr>
  <td>$errata.type$</td>
  <td>$errata.summary$</td>
  <td>$errata.issued$</td>
  <td>$errata.description$</td>
  <td>$if(errata.reboot_suggested)$yes$else$no$endif$</td>
  </tr>
  $endfor$



Host parameter information
==========================

+------------------------------+-----------------------------------------------------+
| Parameter                    | Explanation                                         |
+==============================+=====================================================+
| params.date                  | Maintenance data                                    |
+------------------------------+-----------------------------------------------------+
| params.environment_name      | Host puppet environment name                        |
+------------------------------+-----------------------------------------------------+
| params.ip                    | Host IP address                                     |
+------------------------------+-----------------------------------------------------+
| params.katprep_virt          | Virtualization URI                                  |
+------------------------------+-----------------------------------------------------+
| params.katprep_virt_name     | VM name (*if not FQDN*)                             |
+------------------------------+-----------------------------------------------------+
| params.katprep_virt_snapshot | Flag whether VM needs to be protected by a snapshot |
+------------------------------+-----------------------------------------------------+
| params.katprep_virt_type     | Hypervisor type (*libvirt or pyvmomi*)              |
+------------------------------+-----------------------------------------------------+
| params.location_name         | Location name                                       |
+------------------------------+-----------------------------------------------------+
| params.name                  | Host name                                           |
+------------------------------+-----------------------------------------------------+
| params.operatingsystem_name  | Operating system name                               |
+------------------------------+-----------------------------------------------------+
| params.organization_name     | Organization name                                   |
+------------------------------+-----------------------------------------------------+
| params.owner                 | System owner                                        |
+------------------------------+-----------------------------------------------------+
| params.system_physical       | Flag whether physical system                        |
+------------------------------+-----------------------------------------------------+
| params.time                  | Maintenance time                                    |
+------------------------------+-----------------------------------------------------+

Verification information
========================

+--------------------------------+---------------------------------------------+
| Parameter                      | Explanation                                 |
+================================+=============================================+
| verification.virt_snapshot     | Flag whether snapshot was created           |
+--------------------------------+---------------------------------------------+
| verification.virt_cleanup      | Flag whether snapshot was removed           |
+--------------------------------+---------------------------------------------+
| verification.mon_downtime      | Flag whether downtime was scheduled         |
+--------------------------------+---------------------------------------------+
| verification.mon_cleanup       | Flag whether scheduled downtime was removed |
+--------------------------------+---------------------------------------------+
| verification.mon_status        | Monitoring status                           |
+--------------------------------+---------------------------------------------+
| verification.mon_status_detail | Detailed monitoring status (*if not 0*)     |
+--------------------------------+---------------------------------------------+

