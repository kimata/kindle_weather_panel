#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import yaml
import os

CONFIG_PATH = "../config.yml"


def load_config():
    path = str(pathlib.Path(os.path.dirname(__file__), CONFIG_PATH))
    with open(path, "r") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)
