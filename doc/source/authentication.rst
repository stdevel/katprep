==============
Authentication
==============
Scripts of the **katprep** framework require access to various management systems including:

* Foreman/Katello or Red Hat Satellite 6.x
* Nagios/Icinga or Icinga2
* VMware vSphere / vCenter Server or other hypervisors (*such as Microsoft Hyper-V*)

---------------------
Environment variables
---------------------
To assign login information, the toolkit searches for appropriate environment variables - e.g.:

+-----------------------------+----------------------------------+
| Variable                    | Explanation                      |
+=============================+==================================+
| ``FOREMAN_LOGIN``           | Foreman API user                 |
+-----------------------------+----------------------------------+
| ``FOREMAN_PASSWORD``        | Foreman API password             |
+-----------------------------+----------------------------------+
| ``MONITORING_LOGIN``        | Monitoring API user              |
+-----------------------------+----------------------------------+
| ``MONITORING_PASSWORD``     | Monitoring API password          |
+-----------------------------+----------------------------------+
| ``VIRTUALIZATION_LOGIN``    | Virtualization host API user     |
+-----------------------------+----------------------------------+
| ``VIRTUALIZATION_PASSWORD`` | Virtualization host API password |
+-----------------------------+----------------------------------+

As this is kinda extensive and not very secure at all (*as your login credentials in plain text can be seen in the history of your shell*), it is advisable not to use this mechanism at all.

---------
Prompting
---------
If no environment variables are found, the toolkit prompts for username and password combinations::

   $ katprep_snapshot
   Foreman Username: admin
   Foreman Password:

As it is possible to use multiple hypervisors and monitoring systems for your landscape (*by assigning :doc:`parameters`host parameters*) entering all those authentication information can easily get fiddly. To avoid this, it is advisable to use **authentication containers**.

-------------------------
Authentication containers
-------------------------
Authentication containers are JSON documents containing username/password combinations per host. They are created and edited using ``katprep_authconfig``. If a katprep utility is executed with a specified authentication container and needs access to an external system, it will try to find a username/password combination from the container. If no matching entry is found, the user is prompted.

The following example creates a new authentication container and adds an entry::

   $ katprep_authconfig mycontainer.auth add
   Hostname: simone.giertz.loc
   simone.giertz.loc Username: shittyrobots
   simone.giertz.loc Password: 
   Verify simone.giertz.loc Password: 

You can also specify information with parameters to avoid prompting::

   $ katprep_authconfig mycontainer.auth add -H giertz.stankowic.loc -u cstan -p pinkepank

To display defined entries, use the ``list`` sub-command. The ``-a`` / ``--show-passwords`` parameter will also display passwords::

   $ katprep_authconfig mycontainer.auth list -a
   simone.giertz.loc (Username: shittyrobots / Password: jason)
   giertz.stankowic.loc (Username: cstan / Password: pinkepank)

To remove an entry, use the ``remove`` sub-command::

   $ katprep_authconfig mycontainer.auth remove -H giertz.stankowic.loc

The utility automatically sets permissions **0600** to ensure that the authentication container is only readable by you. If you lower file permissions, the utility will not use this file. Feature version of katprep might include container encryption to enhance security - so, stay tuned.
