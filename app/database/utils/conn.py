# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :uri.py
 @Time      :2022/01/24 15:33
 @Author    :Xuanh.W
 @Usage     :
"""
from Config import globalConfig


def get_db_uri(db_name: str, is_async: bool = False) -> str:
    """
    配置文件中拼接数据库URI
    :param db_name: 数据库名称
    :param is_async: 是否异步，异步则使用asyncpg
    :return:
    """
    host = globalConfig.postgis_db_host
    port = globalConfig.postgis_db_port
    user = globalConfig.postgis_db_user
    passwd = globalConfig.postgis_db_passwd
    return f"postgresql://{user}:{passwd}@{host}:{port}/{db_name}" if not is_async else f"postgresql+asyncpg://{user}:{passwd}@{host}:{port}/{db_name}"

# engine =

if __name__ == "__main__":
    pass
