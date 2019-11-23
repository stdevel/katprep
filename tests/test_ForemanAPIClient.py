#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Foreman API integration
"""

from __future__ import absolute_import

import json
import logging
import pytest
import random
from katprep.clients.ForemanAPIClient import ForemanAPIClient
from katprep.clients import SessionException

from .utilities import load_config


@pytest.fixture
def config():
    return load_config("fman_config.json")


@pytest.fixture
def client(config):
    return ForemanAPIClient(
        logging.ERROR,
        config["config"]["hostname"],
        config["config"]["api_user"],
        config["config"]["api_pass"],
        verify=False
    )


@pytest.fixture
def bookmark_id(client):
    # create demo bookmark
    try:
        client.api_post(
            "/bookmarks", '''
                {
                    "bookmark":
                    {
                        "name": "ForemanAPIClientTest",
                        "controller": "dashboard",
                        "query": "architecture = x86_64",
                        "public": true
                    }
                }'''
        )
    except SessionException as err:
        if "422" not in err:
            # 422 demo content already present
            # We have a problem if it is something different
            raise

    # Retrieving the ID of the previously created bookmark
    bookmarks = json.loads(client.api_get("/bookmarks"))
    for bookmark in bookmarks["results"]:
        if bookmark["name"] == "ForemanAPIClientTest":
            found_id = bookmark["id"]
            break
    else:
        raise RuntimeError("Did not find bookmark!")

    try:
        yield found_id
    finally:

        try:
            client.api_delete("/bookmarks/{}".format(found_id), "")
        except SessionException as err:
            if "404" not in err:
                # 404 means demo content already removed
                # If the error is different we want it shown.
                raise


def test_valid_login(client):
    """
    Ensure exceptions on valid logins
    """
    client.api_get("/architectures")


def test_invalid_login(config):
    """
    Ensure exceptions on invalid logins
    """
    with pytest.raises(SessionException):
        api_dummy = ForemanAPIClient(
            logging.ERROR,
            config["config"]["hostname"],
            "giertz",
            "paulapinkepank",
            verify=False
        )
        # dummy call
        api_dummy.api_get("/status")


def test_api_get(client, bookmark_id):
    """
    Ensure that GET calls are working
    """
    bookmarks = json.loads(client.api_get("/bookmarks/{}".format(bookmark_id)))

    assert bookmarks


def test_api_put(client, bookmark_id):
    """
    Ensure that PUT calls are working
    """
    client.api_put(
        "/bookmarks/{}".format(bookmark_id), '''
            {
                "bookmark": {
                    "name": "ForemanAPIClientTest",
                    "controller": "dashboard",
                    "query": "architecture = i386"
                }
            }'''
    )


def test_api_delete(client, bookmark_id):
    """
    Ensure that DELETE calls are working
    """
    client.api_delete("/bookmarks/{}".format(bookmark_id), "")


def test_api_invalid(client):
    """
    Ensure that dumbass calls will fail
    """
    with pytest.raises(SessionException):
        client.api_get("/giertz/stdevel")


def test_get_name_by_id(client, config):
    """
    Ensure that names can be retrieved by supplying an ID
    """
    for f_obj, f_conf in config["valid_objects"].items():
        assert client.get_name_by_id(f_conf['id'], f_obj)


def test_get_name_by_id_invalid(client, config):
    """
    Ensure that names cannot be retrieving when supplying invalid IDs
    """
    with pytest.raises(SessionException):
        for f_obj, f_conf in config["valid_objects"].items():
            client.get_name_by_id(random.randint(800, 1500), f_obj)


def test_get_id_by_name(client, config):
    """
    Ensure that IDs can be retrieved by supplying an ID
    """
    for f_obj, f_conf in config["valid_objects"].items():
        assert client.get_id_by_name(f_conf['name'], f_obj)


def test_get_id_by_name_invalid(client, config):
    """
    Ensure that names IDs cannot be retrieved by supplying invalid IDs
    """
    with pytest.raises(SessionException):
        for f_obj, f_conf in config["valid_objects"].items():
            vm_name = "giertz{}".format(random.randint(800, 1500))
            client.get_id_by_name(vm_name, f_obj)


def test_get_hostparams(client, config):
    """
    Ensure that host params can be retrieved
    """
    hostparams = client.get_host_params(config["valid_objects"]["host"]["id"])
    assert hostparams


def test_get_hostparams_invalid(client, config):
    """
    Ensure that host params cannot be retrieved by supplying invalid IDs
    """
    with pytest.raises(SessionException):
        client.get_host_params(random.randint(800, 1500))
