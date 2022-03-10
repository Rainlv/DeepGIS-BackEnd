# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :geoserver.py
 @Time      :2022/02/15 15:19
 @Author    :Xuanh.W
 @Usage     :
"""
from pathlib import Path

from utils.constant.geo import LayerType
from Config import rootDir, globalConfig


def get_user_store_name(layer_name: str, layer_type: LayerType):
    ws_suffix_spliter = "_"
    return layer_name + ws_suffix_spliter + layer_type


def get_raster_path(user_name):
    asset_path = Path(rootDir).joinpath(globalConfig.ASSETS_DIR).joinpath(user_name)
    return str(asset_path)