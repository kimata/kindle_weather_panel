#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib
import os
import datetime
import io
import matplotlib
import PIL.Image
import logging

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
from matplotlib.font_manager import FontProperties

from sensor_data import fetch_data

IMAGE_DPI = 100.0


def get_plot_font(config, font_type, size):
    font_path = str(
        pathlib.Path(
            os.path.dirname(__file__), config["PATH"], config["MAP"][font_type]
        )
    )

    logging.info("Load font: {path}".format(path=font_path))

    return FontProperties(fname=font_path, size=size)


def get_face_map(font_config):
    return {
        "title": get_plot_font(font_config, "JP_BOLD", 30),
        "value": get_plot_font(font_config, "EN_COND_BOLD", 64),
        "value_small": get_plot_font(font_config, "EN_COND_BOLD", 40),
        "value_unit": get_plot_font(font_config, "JP_REGULAR", 18),
        "axis": get_plot_font(font_config, "JP_REGULAR", 11),
    }


def plot_item(ax, title, unit, data, xbegin, ylabel, ylim, fmt, small, face_map):
    logging.info("Plot {title}".format(title=title))

    x = data["time"]
    y = data["value"]

    if title is not None:
        ax.set_title(title, fontproperties=face_map["title"], color="#333333")
    ax.set_ylim(ylim)
    ax.set_xlim([xbegin, x[-1] + datetime.timedelta(hours=1)])

    ax.plot(
        x,
        y,
        color="#AAAAAA",
        marker="o",
        markevery=[len(y) - 1],
        markersize=8,
        markerfacecolor="#cccccc",
        markeredgewidth=5,
        markeredgecolor="#666666",
        linewidth=5.0,
        linestyle="solid",
    )

    if not data["valid"]:
        text = "?"
    else:
        text = fmt.format(
            next((item for item in reversed(y) if item is not None), None)
        )

    if small:
        font = face_map["value_small"]
    else:
        font = face_map["value"]

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-H時"))
    for label in ax.get_xticklabels():
        label.set_fontproperties(face_map["axis"])

    for label in ax.get_yticklabels():
        label.set_fontproperties(face_map["axis"])

    ax.set_ylabel(unit, fontproperties=face_map["axis"])

    ax.grid(axis="x", color="#000000", alpha=0.1, linestyle="-", linewidth=1)

    ax.text(
        0.92 - len(unit) * 0.05,
        0.05,
        text,
        transform=ax.transAxes,
        horizontalalignment="right",
        color="#000000",
        alpha=0.8,
        fontproperties=font,
    )

    ax.text(
        0.96,
        0.05,
        unit,
        transform=ax.transAxes,
        horizontalalignment="right",
        color="#000000",
        alpha=0.8,
        fontproperties=face_map["value_unit"],
    )

    ax.label_outer()


def draw_sensor_graph(db_config, config, font_config):
    logging.info("draw sensor graph")

    face_map = get_face_map(font_config)

    room_list = config["ROOM_LIST"]
    width = config["WIDTH"]
    height = config["HEIGHT"]

    plt.style.use("grayscale")

    fig = plt.figure(facecolor="azure", edgecolor="coral", linewidth=2)

    fig.set_size_inches(width / IMAGE_DPI, height / IMAGE_DPI)

    cache = None
    time_begin = datetime.datetime.now(datetime.timezone.utc)
    for row, param in enumerate(config["PARAM_LIST"]):
        for col in range(0, len(room_list)):
            data = fetch_data(
                db_config,
                room_list[col]["TYPE"],
                room_list[col]["HOST"],
                param["NAME"],
            )

            if not data["valid"]:
                continue
            if data["time"][0] < time_begin:
                time_begin = data["time"][0]
            if cache is None:
                cache = {
                    "time": data["time"],
                    "value": [-100.0 for x in range(len(data["time"]))],
                    "valid": False,
                }
                break

    for row, param in enumerate(config["PARAM_LIST"]):
        for col in range(0, len(room_list)):
            data = fetch_data(
                db_config,
                room_list[col]["TYPE"],
                room_list[col]["HOST"],
                param["NAME"],
            )

            if not data["valid"]:
                data = cache

            ax = fig.add_subplot(3, len(room_list), 1 + len(room_list) * row + col)

            if row == 0:
                title = room_list[col]["LABEL"]
            else:
                title = None

            plot_item(
                ax,
                title,
                param["UNIT"],
                data,
                data["time"][0],
                param["UNIT"],
                param["RANGE"],
                param["FORMAT"],
                param["SIZE_SMALL"],
                face_map,
            )

    fig.tight_layout()
    plt.subplots_adjust(hspace=0.1, wspace=0)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=IMAGE_DPI)

    return PIL.Image.open(buf)
