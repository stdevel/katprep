==============
Authentication
==============
Scripts of the **katprep** framework require access to various management systems including:

* Foreman/Katello or Uyuni
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
   File password (max. 32 chars):
   Hostname: simone.giertz.loc
   simone.giertz.loc Username: shittyrobots
   simone.giertz.loc Password: 
   Verify simone.giertz.loc Password: 

You can also specify information with parameters to avoid prompting::

   $ katprep_authconfig mycontainer.auth add -H giertz.stankowic.loc -u cstan -p pinkepank

To display defined entries, use the ``list`` sub-command. The ``-a`` / ``--show-passwords`` parameter will also display passwords::

   $ katprep_authconfig mycontainer.auth list -a
   File password (max. 32 chars):
   simone.giertz.loc (Username: shittyrobots / Password: jason)
   giertz.stankowic.loc (Username: cstan / Password: pinkepank)

To remove an entry, use the ``remove`` sub-command::

   $ katprep_authconfig mycontainer.auth remove -H giertz.stankowic.loc

The utility automatically sets permissions **0600** to ensure that the authentication container is only readable by you. If you lower file permissions, the utility will not use this file.

Encryption
==========
By default, passwords in authentication containers are stored in plain text. It is also possible to use a master password in order to encrypt passwords. When accessing or creating a container, the utility asks for a password::

   $ katprep_authconfig mycontainer.auth add
   File password (max. 32 chars):

The password length can be up to 32 chars. Keep this password safe as you won't be able to read or modify entries without it.
Use the ``password`` sub-command to change the current master password. In the following example, a non-encrypted container will be encrypted::

    $ katprep_authconfig mycontainer.auth password
    File password (max. 32 chars): 
    New file password (max. 32 chars): ...
    Confirm password: ...

It is also possible to utilize the ``-p`` / ``--password`` parameter to specify a container password.
Use an editor of your choice to have a look at the authentication file - the passwords have been encrypted::

    {"myhost": {"username": "giertz", "password": "s/gAAAAABZ..."}}

To remove a master password, simply specify a new empty password::

    $ katprep_authconfig mycontainer.auth password
    File password (max. 32 chars): ...
    New file password (max. 32 chars): 
    {"myhost": {"username": "giertz", "password": "pinkepank"}}
