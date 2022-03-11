# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :geoserver.py
 @Time      :2022/02/15 15:19
 @Author    :Xuanh.W
 @Usage     :
"""
from pathlib import Path

from Config import rootDir, globalConfig


class UserStoreInfo:
    """用户地理数据存储信息"""

    def __init__(self, user_name):
        self._user_name = user_name

    def get_ws_name(self):
        """
        返回该用户的工作空间名称
        :return:
        """
        return self._user_name

    def get_feature_store_name(self):
        """
        返回该用户的工作空间下的POSTGIS矢量数据源名称
        :return:
        """
        return self._user_name

    def get_db_name(self) -> str:
        """
        返回用户数据库名称
        :return:
        """
        return self._user_name


def get_raster_path(user_name):
    asset_path = Path(rootDir).joinpath(globalConfig.ASSETS_DIR).joinpath(user_name)
    return str(asset_path)
