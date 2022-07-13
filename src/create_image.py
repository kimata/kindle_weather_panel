#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
import os
import pathlib
import PIL.Image
import io

from sensor_graph import create_sensor_graph
from weather_panel import create_weather_panel

CONFIG_PATH = "../config.yml"


def load_config():
    path = str(pathlib.Path(os.path.dirname(__file__), CONFIG_PATH))
    with open(path, "r") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


config = load_config()

weather_panel_img = create_weather_panel(config["WEATHER"], config["FONT"])
sensor_graph_img = create_sensor_graph(
    config["INFLUXDB"], config["GRAPH"], config["FONT"]
)

img = PIL.Image.new(
    "L",
    (config["PANEL"]["DEVICE"]["WIDTH"], config["PANEL"]["DEVICE"]["HEIGHT"]),
    "#FFF",
)
img.paste(weather_panel_img, (0, 0))
img.paste(sensor_graph_img, (0, config["WEATHER"]["HEIGHT"]))

bytes_io = io.BytesIO()
img.save(bytes_io, "PNG")
bytes_io.seek(0)

sys.stdout.buffer.write(bytes_io.getvalue())
