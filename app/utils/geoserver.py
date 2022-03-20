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
from exceptions.GeoserverException import NotExistStore
from utils.constant.geo import StoreType


class StoreInfo:
    PUBLIC_STORE = {
        "FEATURE": ["tiger"],
        "RASTER": ["nurc"],
    }
    SHARE_STORE = {
        "FEATURE": ["share"],
        "RASTER": ["share"],
    }

    def __init__(self, store_type: StoreType):
        self.store_type = store_type

    @staticmethod
    def get_store_type_by_name(ws_name, user_name=None):
        """
        根据工作空间名称获取工作空间类型
        :param ws_name:
        :param user_name:
        :return:
        """
        if user_name and ws_name == user_name:
            return StoreType.Private
        elif (ws_name in StoreInfo.PUBLIC_STORE["FEATURE"]) or (ws_name in StoreInfo.PUBLIC_STORE["RASTER"]):
            return StoreType.Public
        elif (ws_name in StoreInfo.SHARE_STORE["FEATURE"]) or (ws_name in StoreInfo.SHARE_STORE["RASTER"]):
            return StoreType.Share
        else:
            raise NotExistStore


class UserStoreInfo(StoreInfo):
    """用户地理数据存储信息"""

    def __init__(self, user_name, store_type: StoreType = StoreType.Private):
        super().__init__(store_type)
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


def get_user_raster_path(user_name):
    asset_path = Path(rootDir).joinpath(globalConfig.ASSETS_DIR).joinpath(user_name)
    return str(asset_path)
