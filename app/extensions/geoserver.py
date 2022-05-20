from loguru import logger
from sqlalchemy_utils import database_exists, create_database

from database.utils.conn import get_db_uri
from utils.geoserver import StoreInfo
from views.map.geoserver import geoserver


async def init_geoserver():
    # create default ws and fs
    public_ws = StoreInfo.PUBLIC_WS
    public_fs = StoreInfo.PUBLIC_STORE['FEATURE']
    if not geoserver.if_ws_exist(public_ws):
        await geoserver.create_workspace(ws=public_ws, exist_ok=True)
        geoserver.create_feature_store(feature_store=public_fs, ws=public_ws, exist_ok=True)

    share_ws = StoreInfo.SHARE_WS
    share_fs = StoreInfo.SHARE_STORE['FEATURE']
    if not geoserver.if_ws_exist(share_ws):
        await geoserver.create_workspace(ws=share_ws, exist_ok=True)
        geoserver.create_feature_store(feature_store=share_fs, ws=share_ws, exist_ok=True)

    await geoserver.init_permission("*.*.w", "*")
    await geoserver.init_permission("*.*.r", "*")

def init_database():
    def create_db_if_not_exists(db_name):
        db_url = get_db_uri(db_name)
        if not database_exists(db_url):
            create_database(db_url, template="template_postgis")
            logger.info(f"创建{db_name}数据库成功！")
        else:
            logger.info(f"database {db_name} already exists, skip creating")

    create_db_if_not_exists(StoreInfo.PUBLIC_DB)
    create_db_if_not_exists(StoreInfo.SHARE_DB)
