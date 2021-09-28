from collections import namedtuple

NVREA = namedtuple("NVREA", "name version release epoch architecture")


def split_rpm_filename(filename: str):
    """
    Splits a standard style RPM file name into NVREA.
    It returns a name, version, release, epoch, arch, e.g.:
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, i386
        1:bar-9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64

    Proudly taken from:
    https://github.com/rpm-software-management/
    yum/blob/master/rpmUtils/miscutils.py

    :param filename: RPM file name
    :type filename: str
    :rtype: NVREA
    """

    if filename[-4:] == ".rpm":
        filename = filename[:-4]

    arch_index = filename.rfind(".")
    arch = filename[arch_index + 1:]

    rel_index = filename[:arch_index].rfind("-")
    rel = filename[rel_index + 1:arch_index]

    ver_index = filename[:rel_index].rfind("-")
    ver = filename[ver_index + 1:rel_index]

    epoch_index = filename.find(":")
    if epoch_index == -1:
        epoch = ""
    else:
        epoch = filename[:epoch_index]

    name = filename[epoch_index + 1:ver_index]
    return NVREA(name, ver, rel, epoch, arch)
