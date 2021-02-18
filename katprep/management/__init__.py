# -*- coding: utf-8 -*-
"""
Clients to access various management systems.
"""

def splitFilename(filename):
    """
    Pass in a standard style rpm fullname 
    
    Return a name, version, release, epoch, arch, e.g.::
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, i386
        1:bar-9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64
    
    Proudly taken from:
    https://github.com/rpm-software-management/
    yum/blob/master/rpmUtils/miscutils.py
    """

    if filename[-4:] == '.rpm':
        filename = filename[:-4]
       
    archIndex = filename.rfind('.')
    arch = filename[archIndex+1:]

    relIndex = filename[:archIndex].rfind('-')
    rel = filename[relIndex+1:archIndex]

    verIndex = filename[:relIndex].rfind('-')
    ver = filename[verIndex+1:relIndex]

    epochIndex = filename.find(':')
    if epochIndex == -1:
        epoch = ''
    else:
        epoch = filename[:epochIndex]
        
    name = filename[epochIndex + 1:verIndex]
    return name, ver, rel, epoch, arch
