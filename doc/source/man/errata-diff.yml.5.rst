NAME
====

**errata-diff.yml** — An individual katprep host maintenance report
variable file

DESCRIPTION
===========

A *errata-diff.yml* file is an individual katprep host maintenance
report variable file used by **katprep\_report(1)** in order to create
host reports. The following information can be found in the variable
file:

-  Generic system information (hostname, IP address,...)
-  Verification data obtained by **katprep\_maintenance(1)**
-  Errata delta information (CVEs, packages,...) between two
   infrastructure snapshot reports created by **katprep\_snapshot(1)**

Usually, these variable files are removed automatically - but for
debugging purposes or writing your own templates it might be necessary
to check the content. To preserve YAML files execute
**katprep\_report(1)** like this:

$ katprep\_report errata\*json -t *template* -x

A valid variable file is written in YAML and contains the following
dictionaries:

-  errata
-  params
-  verification

Every errata entry consists at least of the following variables:

cves
    CVE numbers

description
    Erratum description

errata\_id
    Erratum ID

issued
    Erratum release date

packages
    Dictionary containing related package names

severity
    Erratum severity (bugfix, enhancement, critical)

summary
    Erratum summary

type
    Erratum type (bugfix, enhancement, critical)

The ``params`` section includes at least:

environment\_name
    Puppet environment name

ip
    IP address

katprep\_\*
    katprep-related host parameters

location\_name
    Location the host is assigned to

name
    Object name within Foreman

operatingsystem\_name
    Operating system name

organization\_name
    Organization the host is assigned to

owner
    Specified owner within Foreman

system\_physical
    Flag whether the system is physical

date
    Snapshot creation date

time
    Snapshot creation time

The ``verification`` section can include:

mon\_cleanup
    Flag whether downtime has been cleared

mon\_status
    Overall monitoring state

mon\_status\_detail
    Detailed monitoring state (e.g. service states)

virt\_cleanup
    Flag whether snapshot has been removed

BUGS
====

See GitHub issues: https://github.com/stdevel/katprep/issues

AUTHOR
======

Christian Stankowic info@cstan.io

SEE ALSO
========

**katprep(1)**, **katprep\_maintenance(1)**, **katprep\_report(1)**,
**katprep\_snapshot(1)**
