# !/usr/bin/env Python3
# -*- coding:utf-8 -*-
"""
 @FileName  :Config.py
 @Time      :2022/01/23 23:44
 @Author    :Xuanh.W
 @Usage     :
"""
from pydantic import BaseSettings, IPvAnyAddress, AnyUrl
from dotenv import find_dotenv
from ipaddress import IPv4Address
from pydantic import AnyHttpUrl
from pathlib import Path


class Env(BaseSettings):
    environment: str

    class Config:
        env_file = find_dotenv(".env")
        env_file_encoding = 'utf-8'


class Config(BaseSettings):
    _env_file: str

    # 是否以调试模式运行
    DEBUG: bool = True
    # 程序运行端口
    port: int = 8010

    # 服务器域名/IP
    server_host: str
    # postgis数据库地址
    postgis_db_host: IPvAnyAddress = IPv4Address("127.0.0.1")  # type: ignore
    # postgis数据库端口号
    postgis_db_port: int = 5432
    # postgis数据库用户名
    postgis_db_user: str
    # postgis数据库密码
    postgis_db_passwd: str

    # postgis数据库地址
    geoserver_url: AnyHttpUrl
    # postgis数据库用户名
    geoserver_user: str
    # postgis数据库密码
    geoserver_passwd: str

    DOCKER_BASE_URL: AnyUrl
    DOCKER_CODE_SERVER_DIR: str

    # 用户密码加密盐
    USER_PASSWD_SECRET: str

    # 临时文件
    TMP_DIR: str
    # 用户资源文件夹
    ASSETS_DIR: str

    class Config:
        extra = "allow"
        env_file = find_dotenv(".env.prod")


env = Env()
globalConfig = Config(_env_file=find_dotenv(f".env.{env.environment}"))
rootDir = Path(__file__).resolve().parents[1]
