#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import PIL.Image
import io
import logging

import logger
from sensor_graph import draw_sensor_graph
from weather_panel import draw_weather_panel
from config import load_config

######################################################################
logger.init("E-Ink Weather Panel")

logging.info("start to create image")

config = load_config()

weather_panel_img = draw_weather_panel(config["WEATHER"], config["FONT"])
sensor_graph_img = draw_sensor_graph(
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
