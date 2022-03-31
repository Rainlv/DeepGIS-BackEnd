# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :geoserver.py
 @Time      :2022/01/24 15:58
 @Author    :Xuanh.W
 @Usage     :
"""
from typing import List

import httpx
from geo.Geoserver import Geoserver
from httpx import Response

from Config import globalConfig
from exceptions.GeoserverException import *
from utils.Singleton import Singleton
from loguru import logger


class GeoServerClass(metaclass=Singleton):
    def __init__(self):
        self.geo = Geoserver(service_url=globalConfig.geoserver_url,
                             username=globalConfig.geoserver_user,
                             password=globalConfig.geoserver_passwd)
        self.base_url = f"{globalConfig.geoserver_url}/rest"
        self.client = httpx.AsyncClient(headers={'Accept': "application/json"},
                                        auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd))

    async def create_workspace(self, ws: str, exist_ok: bool = False):
        url = "{}/workspaces".format(self.base_url)
        data = "<workspace><name>{}</name></workspace>".format(ws)
        headers = {"content-type": "text/xml"}
        r: Response = await self.client.post(url=url, data=data,
                                             auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd),
                                             headers=headers)

        if r.status_code == 201:
            logger.info(f"workspace `{ws}` has been created")
            return True

        elif r.status_code == 409:
            msg = f"workspace `{ws}` already exists"
            if exist_ok:
                logger.warning(msg)
            else:
                raise WsExistException(msg)

        else:
            raise CreateWorkspaceException(f"The workspace can not be created, {r.content}")

    def create_feature_store(self, feature_store: str, ws: str, exist_ok: bool = False):
        """
        创建geoserver数据源
        :param feature_store: 数据源名称（与用户名相同，与数据库表名相同）
        :param ws: geoserver工作空间
        :param exist_ok: 已存在处理方式，True忽略，False报错
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
        if not exc_info:
            logger.info(f'{ws}:{feature_store}数据源创建成功')
            return True
        if exc_info.endswith(f"\"Store 'test' already exists in workspace '{feature_store}'\""):
            msg = f"数据源{ws}:{feature_store}已存在！"
            if not exist_ok:
                raise FeatureStoreExistsException(msg)
            else:
                logger.warning(msg)
        else:
            raise CreateFeatureStoreException(f"创建数据源{ws}:{feature_store}失败！" + str(exc_info))

    def if_ws_exist(self, ws: str):
        """工作空间是否存在"""
        exc_info = self.geo.get_workspace(ws)
        return True if exc_info else False

    def if_fs_exist(self, ws: str, fs: str):
        exc_info = self.geo.get_featurestore(store_name=fs, workspace=ws)
        return True if not exc_info.startswith("Error:") else False

    def pub_feature(self, store_name: str, pg_table: str, ws: str):
        exc_info = self.geo.publish_featurestore(workspace=ws, store_name=store_name,
                                                 pg_table=pg_table)
        if exc_info:
            raise PublishFeatureException(f"发布矢量{ws}:{pg_table}:{store_name}失败！" + exc_info)
        logger.info(f'{ws}:{store_name}:{pg_table}矢量发布成功!')

    def pub_raster(self, path: str, ws: str, **kwargs):
        exc_info = self.geo.create_coveragestore(path, workspace=ws, **kwargs)
        if exc_info.startswith("Error: "):
            logger.error(f"发布{ws}:{path}栅格数据失败！错误信息：{exc_info}")
            raise PublishRasterException(exc_info)
        logger.info(f"发布{ws}:{path}栅格数据成功")

    def get_ws_layers(self, ws: str) -> List:
        """
        获取工作空间下的所有图层
        :param ws:
        :return:
        """
        exc_info = self.geo.get_layers(workspace=ws)
        print(exc_info)
        if isinstance(exc_info, str):
            raise GetInfoException(exc_info)
        if exc_info['layers'] == '':
            return []
        layer_ls = [d['name'] for d in exc_info['layers']['layer']]
        return layer_ls

    def get_store_features(self, ws: str, store: str) -> List:
        """
        获取一个数据源下的所有矢量图层
        :param ws:
        :param store:
        :return:
        """
        return self.geo.get_featuretypes(workspace=ws, store_name=store)

    def get_ws_raster_stores(self, ws: str) -> List:
        """
        获取工作空间下所有的栅格数据源
        :param ws:
        :return:
        """
        exc_info = self.geo.get_coveragestores(workspace=ws)
        if isinstance(exc_info, dict):
            return exc_info
        if exc_info.startswith("Error: "):
            logger.error(f"无法获取{ws}的栅格数据源！错误：{exc_info}")
            raise GetInfoException(exc_info)

    async def get_ws_rasters(self, ws: str):
        """
        获取工作空间下的所有栅格图层
        :param ws:
        :return:
        """
        url = f"{self.base_url}/workspaces/{ws}/coverages"
        try:
            r: Response = await self.client.get(url, auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd))
            rasters_infos = r.json()['coverages']
            if not rasters_infos:
                return []
            raster_list = [raster_info['name'] for raster_info in rasters_infos['coverage']]
            return raster_list
        except Exception as e:
            raise GetInfoException(f"获取{ws}栅格图层失败!错误：{e}")

    async def get_ws_features(self, ws: str):
        """
        获取工作空间下的所有矢量图层
        :param ws:
        :return:
        """
        url = f"{self.base_url}/workspaces/{ws}/featuretypes"
        try:
            r: Response = await self.client.get(url, auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd))
            features_infos = r.json()['featureTypes']
            if not features_infos:
                return []
            features_list = [feature_info['name'] for feature_info in features_infos['featureType']]
            return features_list
        except Exception as e:
            raise GetInfoException(f"获取{ws}矢量图层失败!错误：{e}")

    async def delete_workspace(self, ws: str):
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}".format(self.base_url, ws)
        r: Response = await self.client.delete(url,
                                               auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd),
                                               params=payload)

        if r.status_code == 200:
            logger.info(f"Workspace `{ws}` has been deleted successfully")
        elif r.status_code == 404:
            raise WsNotExistsException(f"Can't delete workspace `{ws}`, do not exists!")
        else:
            raise DeleteWorkspaceException(f"Can't delete workspace `{ws}`, {r.status_code}")

    async def delete_ws_if_exists(self, ws: str):
        if not self.if_ws_exist(ws=ws):
            logger.warning(f"`{ws}` do not exists, skip deleting")
            return False
        else:
            await self.delete_workspace(ws)
            return True

    async def delete_featurestore(self, feature_store: str, ws: str):
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.base_url, ws, feature_store
        )
        r: Response = await self.client.delete(
            url, auth=(globalConfig.geoserver_user, globalConfig.geoserver_passwd), params=payload
        )
        if r.status_code == 200:
            logger.info(f"删除{ws}:{feature_store}成功")

        elif r.status_code == 404:
            raise NotExistStore(f"删除{ws}:{feature_store}失败, 该数据源不存在")
        else:
            raise DeleteFeatureStoreException(f"删除{ws}:{feature_store}失败")

    async def delete_fs_if_exists(self, fs: str, ws: str):
        if not self.if_fs_exist(ws=ws, fs=fs):
            logger.warning(f"`{ws}:{fs}`do not exists, skip deleting")
        else:
            await self.delete_featurestore(feature_store=fs, ws=ws)
            return True

    def delete_layer(self, layer_name: str, ws: str):
        try:
            exc_info = self.geo.delete_layer(layer_name=layer_name, workspace=ws)
            if exc_info.startswith("Error: "):
                raise Exception(exc_info)
        except Exception as e:
            logger.error(f"删除{ws}工作区的{layer_name}图层失败！错误：{e}")
            raise DeleteLayerException(str(e))


geoserver = GeoServerClass()

if __name__ == '__main__':
    import asyncio

    print(geoserver.delete_featurestore(ws='public', feature_store="test"))
    # user_name = "cite1_feature"
    # geoserver.delete_workspace(user_name)
    # print(asyncio.run(geoserver.delete_ws_if_exists('test1')))
