=========
Changelog
=========
This page shows changes of the latest releases.

-------------
Version 0.5.0
-------------
Release date: **yyyy/mm/dd**

.. note:: Red Hat Satellite 6.x users need to update to version 6.3 in order to enable VM reboots after system maintenance. Also, you will need to ensure that your virtualization infrastructure is registered within Foreman to link VMs to hosts.

Changes since previous development releases:

katprep_maintenance
===================
* added posibility to suppress reboots under any circumstances (`issue39`_)
* changed default reboot behavior to only reboot if erratum suggests it (`issue39`_)
* fixed a bug where errata were tried to install if no errata were applicable (`issue39`_)
* fixed a bug where enabled reboots were executed before gracefully completing errata installation (`issue40`_)
* implemented ``-p`` / ``--include-packages`` parameters to also include non-erratum package upgrades during maintenance (`issue33`_)
* implemented ``-E`` / ``--exclude`` parameters to exclude particular hosts by hostname wildcards (`issue38`_)
* fixed bug where non-existent snapshots forced crashes
* implemented ``-I`` / ``--include-only`` parameters to only include particular hosts by hostname wildcards (`issue63`_)
* implemented ``revert`` command (`issue6`_)

.. _issue6: https://github.com/stdevel/katprep/issues/6
.. _issue33: https://github.com/stdevel/katprep/issues/33
.. _issue38: https://github.com/stdevel/katprep/issues/38
.. _issue39: https://github.com/stdevel/katprep/issues/39
.. _issue40: https://github.com/stdevel/katprep/issues/40
.. _issue63: https://github.com/stdevel/katprep/issues/63

katprep_snapshot
================
* fixed a bug where detecting physical hosts was not working properly (`issue44`_)
* fixed a bug where unregistered content hosts forced crashes (`issue52`_)
* changed missing key log facility to debug 
* fixed a bug where hostnames were not verified
* fixed a bug where ``reboot_required`` flags were not set correctly (`issue61`_)
* fixed a bug where physical host/VMs flags were not set correctly (`issue61`_)

.. _issue44: https://github.com/stdevel/katprep/issues/44
.. _issue52: https://github.com/stdevel/katprep/issues/52
.. _issue61: https://github.com/stdevel/katprep/issues/61

katprep_populate
================
* implemented a IPv6 filter (`issue35`_)

.. _issue35: https://github.com/stdevel/katprep/issues/35

API integrations
================
* All: implemented unit tests for API clients (`issue13`_)
* NagiosCGIClient, Icinga2APIClient, PyvmomiClient: implemented IPv4/6 filters
* NagiosCGIClient: fixed a bug where scheduling downtime for hosts was not possible (`issue41`_)
* NagiosCGIClient: implemented Nagios legacy detection throwing execptions for non-supported actions (`issue41`_)
* NagiosCGIClient: fixed several bugs where web-scraping was not working properly forcing incorrect results (`issue41`_)
* NagiosCGIClient: fixed a bug where scheduling downtimes was not possible
* NagiosCGIClient: made ``has_downtime()`` more efficient and overhauled webscraping (`issue64`_)
* SpacewalkAPIClient: first integration stubs
* ForemanAPIClient, SpacewalkAPIClient: Moved hostname verification to shared library

.. _issue13: https://github.com/stdevel/katprep/issues/13
.. _issue41: https://github.com/stdevel/katprep/issues/41
.. _issue64: https://github.com/stdevel/katprep/issues/64

Shared library
==============
* added parameters ``-P`` / ``--auth-password`` for pre-defining authentication container password (`issue36`_)

.. _issue36: https://github.com/stdevel/katprep/issues/36

Miscellaneous
=============
* added manpages (`issue11`_)

.. _issue11: https://github.com/stdevel/katprep/issues/11
