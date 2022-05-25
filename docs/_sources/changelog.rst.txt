=========
Changelog
=========
This page shows changes of the latest releases.

-------------
Version 0.6.x
-------------
Release date: **2022/xx/xx**

.. warning:: This is a development version that most likely breaks Red Hat Satellite support. The next version will re-implement this support.

Changes since previous development releases:

General
=======
* **Uyuni / SUSE Manager support implemented** (`issue43`_)
* **Pre/post script suuport implemented** (`issue123`_)
* Python 2.7 is dropped, at least Python 3.6 is required (`issue125`_)
* cleaned-up code heavily
* simplified contributions by supplying a Vagrant configuration and Ansible code (`issue108`_)
* use relative imports
* make code more modular by implementing abstract base classes
* added code coverage (`issue96`_)
* fixed a bug where modules couldn't be executed directly (`issue97`_)
* renamed ``dummy_call`` to ``is_authenticated`` (`issue102`_)
* replaced ``mock`` with ``unittest.mock`` (`issue156`_)

.. _issue43: https://github.com/stdevel/katprep/issues/43
.. _issue96: https://github.com/stdevel/katprep/issues/96
.. _issue97: https://github.com/stdevel/katprep/issues/97
.. _issue102: https://github.com/stdevel/katprep/issues/102
.. _issue108: https://github.com/stdevel/katprep/issues/108
.. _issue123: https://github.com/stdevel/katprep/issues/123
.. _issue125: https://github.com/stdevel/katprep/issues/125
.. _issue156: https://github.com/stdevel/katprep/issues/156

katprep_authconfig
==================
* fixed a bug where utilizing encrypted authentication containers wasn't possible (`issue85`_)
* fixed a bug where ``katprep_authconfig`` wasn't working in Python 3.6 (`issue150`_)

.. _issue85: https://github.com/stdevel/katprep/issues/85
.. _issue150: https://github.com/stdevel/katprep/issues/150

katprep_maintenance
===================
* fixed a bug where trying to remove already removed snapshots crashed with EmptySetException (`issue90`_)

.. _issue90: https://github.com/stdevel/katprep/issues/90

katprep_snapshot
================
* fixed a bug where filtering using the organization name wasn't working (`issue94`_)

.. _issue94: https://github.com/stdevel/katprep/issues/94

-------------
Version 0.5.0
-------------
Release date: **2018/06/29**

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

katprep_report
==============
* fixed several bugs where report information were incorrect (`issue61`_)

.. _issue61: https://github.com/stdevel/katprep/issues/61

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
* Icinga2APIClient: Fixed a bug where some information were not retrieved correctly (`issue60`_)

.. _issue13: https://github.com/stdevel/katprep/issues/13
.. _issue41: https://github.com/stdevel/katprep/issues/41
.. _issue60: https://github.com/stdevel/katprep/issues/60
.. _issue64: https://github.com/stdevel/katprep/issues/64

Shared library
==============
* added parameters ``-P`` / ``--auth-password`` for pre-defining authentication container password (`issue36`_)

.. _issue36: https://github.com/stdevel/katprep/issues/36

Miscellaneous
=============
* added manpages (`issue11`_)

.. _issue11: https://github.com/stdevel/katprep/issues/11
