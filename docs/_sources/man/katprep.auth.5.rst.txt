NAME
====

**katprep.auth** — An individual katprep authentication container file

DESCRIPTION
===========

A *katprep.auth* file is an individual authentication container file
used by the **katprep(1)** framework in order to gain access to external
third-party systems (such as monitoring systems and hypervisors). This
removes the need of entering login information every time to trigger
external systems. Authentication containers are JSON documents that can
also be protected by a passphrase. In this case, you need to enter the
passphrase once when using the container.

A valid document contains a dictionary containing hostnames and another
dictionary specifying the following fields:

username
    A valid username

password
    Appropriate password

    Example:

{"vcenter.giertz.loc": {"username": "stdevel", "password": "chad"}

Once encrypted, corresponding password entries are replaced with
symmetric Fernet hashes:

{"vcenter.giertz.loc": {"username": "stdevel", "password": "s/gAAAA..."}

To modify an authentication container, utilize the
**katprep\_authconfig(1)** utility - manually editing the file is **not
supported**.

BUGS
====

See GitHub issues: https://github.com/stdevel/katprep/issues

AUTHOR
======

Christian Stankowic info@cstan.io

SEE ALSO
========

**katprep(1)**, **katprep\_authconfig(1)**
