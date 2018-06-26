% katprep_authconfig(1) Version 0.5.0 | katprep documentation

NAME
====

**katprep_authconfig** — manages credentials for third-party systems triggered by katprep

SYNOPSIS
========

| **katprep_authconfig** \[**-h**] \[**-v**] \[**-q**] \[**-d**] \[_file_] \[**list**|**add**|**remove**|**password**]

DESCRIPTION
===========

Creates, modifies and removes entries from authentication containers used by the katprep framework in order to gain access to external third-party systems (such as monitoring systems and hypervisors). This removes the need of entering login information every time to trigger external systems.
Authentication containers are JSON documents that can also be protected by a passphrase. In this case, you need to enter the passphrase once when using the container.

Options
-------

-h, --help

:   Prints brief usage information.

-v, --version

:   Prints the current version number.

-q, --quiet

:   Supresses printing status messages to stdout.

-d, --debug

:   Enables debugging outputs.

Listing credentials
-------------------

To list credentials, use the **list** command. By default, the output will contain hostnames and usernames, but no password. To also show password in plain text, add the following parameter:

-a, --show-password
:    also print passwords.

Adding credentials
------------------

To add credentials, use the **add** command. By default, you will be prompted for hostname, username and password. To pre-select information, utilize the following parameters:

-H _hostname_, --hostname _hostname_

:   Third-party system hostname

-u _username_, --username _username_

:   Appropriate username

-p _password_, --password _password_

:   Corresponding password

Removing credentials
--------------------

To remove credentials, use the **remove** command. You will be prompted for a hostname, to pre-select the hostname, utilize the following parameter:

-H _hostname_, --hostname _hostname_

:   Third-party system hostname

Encrypting/decrypting containers
--------------------------------

By default, authentication containers contain login information in plain text. To enhance security, it is possible to encrypt the passwords with a passphrase up to 32 chars. To encrypt or decrypt a file, utilize the **password** command. By default, the utility prompts a password. To pre-select the password, utilize the following parameter:

-p _password_, --password _password_

:   Password

To encrypt an authentication container, simply execute **katprep_authconfig** \[_file_] **password** and specify a passphrase. To remove the encryption, re-run the command without specifying a passphrase. 

FILES
=====

*~/.katpreprc*

:   Per-user katprep configuration file.

*katprep.auth*

:   Individual katprep authentication container file.

BUGS
====

See GitHub issues: <https://github.com/stdevel/katprep/issues>

AUTHOR
======

Christian Stankowic <info@cstan.io>

SEE ALSO
========

**katprep.auth(5)**
