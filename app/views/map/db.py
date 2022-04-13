from io import BytesIO
from typing import List

from geopandas import GeoDataFrame
from sqlalchemy import MetaData, Table, Column, Integer, create_engine, text, bindparam
from geoalchemy2 import Geometry
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions import database_exists, create_database
import aiofiles

from Config import globalConfig, rootDir
from utils.constant.geo import GeoType, LayerType
from database.utils.conn import get_db_uri
from exceptions.DatabaseException import TableCreateException, DatabaseCreateException
from loguru import logger
import geopandas as gpd
from pathlib import Path

# TODO 异步重写
from utils.geoserver import get_user_raster_path, UserStoreInfo
from views.map.geoserver import geoserver


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


def upload2postGIS(file, filename, user_name: str, isZip: bool = False, **kwargs):
    feature_file = gpd.read_file(file)
    # 将 几何信息的列 重命名为 the_gemo 与Geoserver相同，方便读取
    feature_file.rename_geometry('the_geom', inplace=True)
    store_info = UserStoreInfo(user_name)
    db_uri = get_db_uri(store_info.get_db_name())
    engine = create_engine(db_uri)
    # TODO 异常捕获
    filename_without_suffix = Path(filename).with_suffix('')
    feature_file.to_postgis(str(filename_without_suffix), con=engine, **kwargs)
    geoserver.pub_feature(store_name=store_info.get_feature_store_name(), pg_table=filename_without_suffix,
                          ws=store_info.get_ws_name())


# TODO 分块读取优化
def download_from_postGIS(table_name: str, db_name: str, out_file_type: str = None, **kwargs) -> BytesIO:
    """
    读取数据库中的矢量，返回二进制流
    :param table_name: 表名
    :param db_name: 数据库名
    :param out_file_type: 输出文件类型，默认为shp，否则应为OGR format driver，参考 https://gdal.org/drivers/vector/index.html
    :return: 矢量的二进制流对象
    """
    db_uri = get_db_uri(db_name)
    engine = create_engine(db_uri)
    feature_df = gpd.read_postgis(table_name, geom_col='the_geom', con=engine, **kwargs)
    byte_stream = BytesIO()
    feature_df.to_file(byte_stream, driver=out_file_type)
    byte_stream.seek(0)
    return byte_stream


def _zip_shpFiles(feature_df: GeoDataFrame):
    pass


# FIXME SQL注入问题
def delete_feature_asset(table_name: str, db_name: str):
    # sql = text('DROP TABLE IF EXISTS :table_name')
    sql = text(f'DROP TABLE IF EXISTS {table_name}')
    db_uri = get_db_uri(db_name)
    engine = create_engine(db_uri)
    # result = engine.execute(sql, table_name=table_name)
    result = engine.execute(sql)
    geoserver.delete_layer(table_name, ws=db_name)


class RasterGeo:
    def __init__(self, user_name):
        self.user_name = user_name
        self.store_info = UserStoreInfo(user_name)

    async def do_upload(self, layer_name, file_content):
        layer_name = Path(layer_name).stem
        await geoserver.pub_raster(file=file_content, ws=self.store_info.get_ws_name(), layer_name=layer_name)


if __name__ == "__main__":
    import asyncio

    # with open('example.geojson', 'rb') as r:
    #     upload2postGIS(r, 'test_upload_bytes', 'test_user')
    # with open('t', 'wb') as w:
    # download_from_postGIS(table_name="test_upload_hsg", db_name='test_user', out_file_type='ESRI Shapefile')
    with open(r'D:\OneDrive - webmail.hzau.edu.cn\桌面\tdly_2015.tif', 'rb') as f:
        content = f.read()
    uploader = RasterGeo('foo')
    asyncio.run(uploader.do_upload('test1.tif', content))
