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
def virt_config_file(virtualisation):
    if virtualisation == 'libvirt':
        return "libvirt_config.json"
    elif virtualisation == 'pyvmomi':
        return "pyvmomi_config.json"


@pytest.fixture
def virt_config(virt_config_file):
    return load_config(virt_config_file)


@pytest.fixture
def virt_class(virtualisation):
    if virtualisation == 'libvirt':
        libvirt_client = pytest.importorskip("katprep.clients.LibvirtClient")
        return libvirt_client.LibvirtClient
    elif virtualisation == 'pyvmomi':
        pyvmomi_client = pytest.importorskip("katprep.clients.PyvmomiClient")
        return pyvmomi_client.PyvmomiClient


@pytest.fixture
def virt_client(virtualisation, virt_config, virt_class):
    if virtualisation == 'libvirt':
        address = virt_config["config"]["uri"],
    elif virtualisation == 'pyvmomi':
        address = virt_config["config"]["hostname"],

    return virt_class(
        logging.ERROR,
        address,
        virt_config["config"]["api_user"],
        virt_config["config"]["api_pass"]
    )
