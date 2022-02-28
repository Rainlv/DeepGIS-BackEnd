# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :geoserver.py
 @Time      :2022/01/24 15:58
 @Author    :Xuanh.W
 @Usage     :
"""
from geo.Geoserver import Geoserver
from Config import globalConfig
from exceptions.GeoserverException import CreateFeatureStoreException, PublishFeatureException, \
    CreateWorkspaceException, GetFeatureInfoException, DeleteWorkspaceException, DeleteFeatureStoreException
from utils.Singleton import Singleton
from loguru import logger


class GeoServerClass(metaclass=Singleton):
    def __init__(self):
        self.geo = Geoserver(service_url=globalConfig.geoserver_url,
                             username=globalConfig.geoserver_user,
                             password=globalConfig.geoserver_passwd)

    def create_workspace(self, ws: str):
        try:
            exc_info = self.geo.create_workspace(ws)
            if exc_info.startswith("Error: "):
                raise CreateWorkspaceException(exc_info)
            logger.info(f'{ws}工作空间创建成功')
        except Exception as e:
            raise CreateWorkspaceException(f"创建工作区{ws}失败！" + str(e))

    def create_feature_store(self, feature_store: str, ws: str):
        """
        创建geoserver数据源
        :param feature_store: 数据源名称（应于用户名相同）
        :param ws: geoserver工作空间
        :return:
        """
        exc_info = self.geo.create_featurestore(store_name=feature_store,
                                                workspace=ws,
                                                db=feature_store,
                                                host=globalConfig.postgis_db_host,
                                                port=globalConfig.postgis_db_port,
                                                pg_user=globalConfig.postgis_db_user,
                                                pg_password=globalConfig.postgis_db_passwd,
                                                )
        if exc_info:
            raise CreateFeatureStoreException(f"创建数据源{ws}:{feature_store}失败！" + str(exc_info))
        logger.info(f'{ws}:{feature_store}数据源创建成功')

    def pub_feature(self, feature_name: str, feature_store: str, ws: str):
        exc_info = self.geo.publish_featurestore(workspace=ws, store_name=feature_store,
                                                 pg_table=feature_name)
        if exc_info:
            raise PublishFeatureException(f"发布矢量{ws}:{feature_store}:{feature_name}失败！" + exc_info)
        logger.info(f'{ws}:{feature_store}:{feature_name}矢量发布成功!')

    def get_ws_features(self, ws: str):
        exc_info = self.geo.get_layers(workspace=ws)
        if isinstance(exc_info, str):
            raise GetFeatureInfoException(exc_info)
        if exc_info['layers'] == '':
            return []
        layer_ls = [d['name'] for d in exc_info['layers']['layer']]
        return layer_ls

    def delete_workspace(self, ws: str):
        try:
            exc_info = self.geo.delete_workspace(ws)
            if exc_info.startswith("Error: "):
                raise Exception(exc_info)
            logger.info(f"删除{ws}工作区成功")
        except Exception as e:
            logger.error(f"删除{ws}工作区失败！错误：{e}")
            raise DeleteWorkspaceException(str(e))

    def delete_featurestore(self, feature_store: str, ws: str):
        try:
            exc_info = self.geo.delete_featurestore(featurestore_name=feature_store, workspace=ws)
            if exc_info.startswith("Error: "):
                raise Exception(exc_info)
        except Exception as e:
            logger.error(f"删除{ws}工作区的{feature_store}数据源失败！错误：{e}")
            raise DeleteFeatureStoreException(str(e))


geoserver = GeoServerClass()
if __name__ == '__main__':
    user_name = "cite1_feature"
    geoserver.delete_workspace(user_name)
