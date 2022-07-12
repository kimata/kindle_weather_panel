#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
import os
import pathlib
import PIL.Image
import io
import wsgiref.handlers
import time
from requests import Request, Session
import hmac
import hashlib
import base64

from sensor_graph import create_sensor_graph
from weather_panel import create_weather_panel

CONFIG_PATH = "../config.yml"


def load_config():
    path = str(pathlib.Path(os.path.dirname(__file__), CONFIG_PATH))
    with open(path, "r") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


def upload(img_stream, server_ip, uuid, api_secret, api_key):
    method = "PUT"
    api = "/backend/{uuid}".format(uuid=uuid)

    headers = {
        "Date": wsgiref.handlers.format_date_time(time.time()),
    }

    req = Request(
        method,
        "http://{server_ip}:8081{api}".format(server_ip=server_ip, api=api),
        files=[("image", ("weather.png", img_stream, "image/png"))],
        headers=headers,
    )

    prepped = req.prepare()

    h = hmac.new(
        api_secret.encode("utf-8"),
        "{method}\n\n{content_type}\n{date}\n{api}".format(
            method=method,
            content_type=prepped.headers["Content-Type"],
            date=headers["Date"],
            api=api,
        ).encode("utf-8"),
        hashlib.sha256,
    )

    prepped.headers["Authorization"] = (
        api_key + ":" + (base64.encodebytes(h.digest()).strip()).decode("utf-8")
    )

    return Session().send(prepped)


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
