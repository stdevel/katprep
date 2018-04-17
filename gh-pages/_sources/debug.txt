==========================
Debugging and getting help
==========================

This software is at an early stage, so perhaps things might explode. This page describes how to get in touch with the development team to get help.

------------
Getting help
------------
Basically, the best idea when having problems is to open an issue on GitHub_. Please supply the following information:
 - the Foreman/Katello or Red Hat Satellite version you are using
 - the katprep version you're using
 - a short description of your landscape (*e.g. single Foreman instance with some VMs running on a single ESXi host*)
 - debugging output of the command you're facing errors with (*see also Debugging*) - please attach a file instead of pasting the console output directly in the issue

With these information it is easier to reproduce the error you're reporting.

.. _GitHub: https://github.com/stdevel/katprep/issues

---------
Debugging
---------
Every katprep command offers a ``-d`` / ``--debug`` parameter. When investigating on an error, use this parameter to enable debugging outputs. Keep in mind, that the output will be quite long, so using these parameters along with ``tee`` is basically a good idea::

 $ katprep_snapshot -C mycontainer.auth -s myforeman.giertz.loc -d 2>&1 | tee myerror.log

This command will dump all standard and error output into a file named ``myerror.log``. When opening an issue on GitHub, please attach this file.

-------------
Common issues
-------------
Please checkout the issues_ page - it contains some common issues and how to fix them.

.. _issues: issues.html
