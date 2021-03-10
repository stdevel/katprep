#! -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import pytest

from .utilities import load_config


@pytest.fixture
def nonexisting_vm():
    return "giertz.pinkepank.loc"


@pytest.fixture
def snapshot_name(virtualisation):
    if virtualisation == 'libvirt':
        return "LibvirtClientTest"
    elif virtualisation == 'pyvmomi':
        return "PyvmomiClientTest"


@pytest.fixture(params=['libvirt', 'pyvmomi'])
def virtualisation(request):
    return request.param


@pytest.fixture
def virtConfigFile(virtualisation):
    if virtualisation == 'libvirt':
        return "libvirt_config.json"
    elif virtualisation == 'pyvmomi':
        return "pyvmomi_config.json"


@pytest.fixture
def virtConfig(virtConfigFile):
    return load_config(virtConfigFile)


@pytest.fixture
def virtClass(virtualisation):
    if virtualisation == 'libvirt':
        libvirt = pytest.importorskip("katprep.virtualization.libvirt")
        return libvirt.LibvirtClient
    elif virtualisation == 'pyvmomi':
        vmware = pytest.importorskip("katprep.virtualization.vmware")
        return vmware.PyvmomiClient


@pytest.fixture
def virtClient(virtualisation, virtConfig, virtClass):
    if virtualisation == 'libvirt':
        address = virtConfig["config"]["uri"],
    elif virtualisation == 'pyvmomi':
        address = virtConfig["config"]["hostname"],

    return virtClass(
        logging.ERROR,
        address,
        virtConfig["config"]["api_user"],
        virtConfig["config"]["api_pass"]
    )
