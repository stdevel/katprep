# Documentation

Currently, both manpages and product documentation are part of this repository (*this will change in the future*).

To update the product documentation, run the `publish.sh` script. It will update the `docs` directory in the previous level. The sources are part of the [`source`](source) directory.

To update manpages, change to the `manpages` directory and run the `make` command. Manpages are created from Markdown using `pandoc`, the sources are located in the [`manpages/src`](manpages/src) directory.
