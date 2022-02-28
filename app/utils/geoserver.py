# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :geoserver.py
 @Time      :2022/02/15 15:19
 @Author    :Xuanh.W
 @Usage     :
"""
from utils.constant.geo import LayerType


def get_user_ws_name(layer_name: str, layer_type: LayerType):
    ws_suffix_spliter = "_"
    return layer_name + ws_suffix_spliter + layer_type
