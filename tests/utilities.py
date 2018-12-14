# -*- coding: utf-8 -*-

import json
import os
import pytest


def load_config(config_file):
    if not os.path.isfile(config_file):
        pytest.skip("Please create configuration file %s!" % config_file)

    try:
        with open(config_file, "r") as json_file:
            return json.load(json_file)
    except IOError as err:
        pytest.skip("Unable to read configuration file: '%s'", err)
