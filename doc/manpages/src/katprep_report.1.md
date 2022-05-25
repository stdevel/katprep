% katprep_report(1) Version 0.6.0 | katprep documentation

# NAME

**katprep_report** — Creates reports after system maintenance

# SYNOPSIS

| **katprep_report** \[**-h**] \[**--version**] \[**-q**] \[**-d**] \[**-p** _path_] \[**-o** _path_] \[**-x**] \[**-t** _file_] _snapshot\_file_ _snapshot\_file_

# DESCRIPTION

Creates reports after system maintenance based on two infrastructure status snapshots created by **katprep_snapshot(1)**. The utility will automatically detect previous and current snapshots by checking the report change times.

Run this utility after maintaining systems using **katprep_maintenance(1)**.

## Options

-h, --help

:   Prints brief usage information.

--version

:   Prints the current version number.

-q, --quiet

:   Supresses printing status messages to stdout.

-d, --debug

:   Enables debugging outputs.

-p _path_, --output-path _path_

:   Defines the report output path (default: current directory)

-C _filename_, --auth-container _filename_

:   Defines an authentication container file (see also **katprep.auth(5)** and **katprep_authconfig(1)**)

-o _type_, --output-tpe _type_

:   Defines the Pandoc output file type, usually this is set automatically based on the template file extension (default: no)

-x, --preserve-yaml

:   Keeps the YAML metadata after creating the reports, useful for debugging (default: no)

-t _file_, --template _file_

:   Defined the Pandoc template to use

# FILES

*~/.katpreprc*

:   Per-user katprep configuration file.

*katprep.auth*

:   Individual katprep authentication container file.

# BUGS

See GitHub issues: <https://github.com/stdevel/katprep/issues>

# AUTHOR

Christian Stankowic <info@cstan.io>

# SEE ALSO

**katprep(1)**, **errata-diff.yml(5)**, **katprep_maintenance(1)**, **katprep_snapshot(1)**
