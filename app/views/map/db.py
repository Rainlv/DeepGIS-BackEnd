from typing import List

from sqlalchemy import MetaData, Table, Column, Integer, create_engine
from geoalchemy2 import Geometry
from sqlalchemy_utils.functions import database_exists, create_database, drop_database

from utils.constant.geo import GeoType
from database.utils.uri import get_db_uri
from exceptions.DatabaseException import TableCreateException, DatabaseCreateException
from loguru import logger


# TODO 异步重写
def create_geo_table(db_name, table_name, geo_type: GeoType, fields: List[Column] = []):
    db_uri = get_db_uri(db_name)
    engine = create_engine(db_uri)
    metadata = MetaData()
    tb = Table(table_name, metadata,
               Column("FID", Integer, primary_key=True),
               Column("the_geom", Geometry(geometry_type=geo_type.value, srid=4326))
               )
    for field in fields:
        tb.append_column(field)
    if engine.dialect.has_table(engine.connect(), table_name):
        raise TableCreateException(f"创建{table_name}表失败！表{table_name}已存在！")
    try:
        tb.create(engine, checkfirst=True)
    except Exception as e:
        raise TableCreateException(f"创建{table_name}表失败！" + str(e))
    logger.info(f'创建{db_name}:{table_name}矢量表成功！\n'
                f'\t矢量类型:{geo_type}')
    return tb


# TODO 异步重写,用户名预处理（防止不合法的数据库名）
def create_user_database(db_name):
    """
    创建用户个人数据库
    :param db_name: 用户名即数据库名
    :return:
    """
    db_url = get_db_uri(db_name)
    if not database_exists(db_url):
        create_database(db_url, template="template_postgis")
        logger.info(f"创建{db_name}数据库成功！")

    else:
        raise DatabaseCreateException(f"数据库{db_name}已存在！")


if __name__ == "__main__":
    create_user_database("test_user")
    # create_geo_table("test_db2", "test_shp1", GeoType.POINT)
