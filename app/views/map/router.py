from fastapi import APIRouter, Depends, File, UploadFile

from Schemas.Geoserver import CreateTable
from Schemas.Response import BaseResponse
from utils.geoserver import UserStoreInfo, StoreInfo
from views.map.db import create_geo_table, upload2postGIS, delete_feature_asset, RasterGeo
from sqlalchemy import Column
import sqlalchemy
from views.map.geoserver import geoserver as geoserver_instance
from views.user.models import User
from views.user.users import current_user

router = APIRouter(tags=['geoserver'], prefix="/geoserver")


@router.post("/create_table")
async def _(param: CreateTable, user: User = Depends(current_user())):
    user_name = user.nick_name
    store_info = UserStoreInfo(user_name)
    table_name = param.layer_name
    geo_type = param.geo_type
    fields_list = param.fields
    field_cols = []
    for field in fields_list:
        field_type_str = field.field_type
        field_name = field.field_name
        field_type = getattr(sqlalchemy, field_type_str)
        field_col = Column(field_name, field_type)
        field_cols.append(field_col)
    create_geo_table(db_name=store_info.get_db_name(), table_name=table_name, geo_type=geo_type, fields=field_cols)
    geoserver_instance.pub_feature(store_name=store_info.get_feature_store_name(), pg_table=table_name,
                                   ws=store_info.get_ws_name())
    return BaseResponse(
        code=0,
        message=""
    )


@router.get("/get_user_features")
async def _(user: User = Depends(current_user())):
    user_name = user.nick_name
    store_info = UserStoreInfo(user_name)
    user_ws = store_info.get_ws_name()
    public_ws = StoreInfo.PUBLIC_WS
    share_ws = StoreInfo.SHARE_WS
    user_feature_result = await geoserver_instance.get_ws_features(ws=user_ws)
    user_raster_result = await geoserver_instance.get_ws_rasters(ws=user_ws)
    public_feature_result = await geoserver_instance.get_ws_features(ws=public_ws)
    public_raster_result = await geoserver_instance.get_ws_rasters(ws=public_ws)
    share_feature_result = await geoserver_instance.get_ws_features(ws=share_ws)
    share_raster_result = await geoserver_instance.get_ws_rasters(ws=share_ws)
    return BaseResponse(
        code=0,
        message='',
        result=[
            {"id": "user", "label": "我的资源",
             "children": [
                 {
                     "id": "user_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"{user_ws}:{feature_name}", "label": feature_name, "type": "feature"}
                         for feature_name in user_feature_result]
                 },
                 {
                     "id": "user_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"{user_ws}:{raster_name}", "label": raster_name, "type": "raster"}
                         for raster_name in user_raster_result]},
             ]},
            {"id": "public", "label": "公共资源",
             "children": [
                 {
                     "id": "public_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"{public_ws}:{feature_name}",
                          "label": feature_name, "type": "feature"}
                         for feature_name in public_feature_result]},
                 {
                     "id": "public_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"{share_ws}:{raster_name}", "label": raster_name, "type": "raster"}
                         for raster_name in public_raster_result]},
             ]},
            {"id": "share", "label": "共享资源",
             "children": [
                 {
                     "id": "share_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"share:{feature_name}",
                          "label": feature_name, "type": "feature"}
                         for feature_name in share_feature_result]},
                 {
                     "id": "share_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"share:{raster_name}", "label": raster_name, "type": "raster"}
                         for raster_name in share_raster_result]},
             ]},
        ]
    )


@router.post('/upload_shp')
async def _(file: UploadFile = File(...), user: User = Depends(current_user())):
    upload2postGIS(file.file, filename=file.filename, user_name=user.nick_name)
    return BaseResponse(
        code=0,
        message='',
    )


@router.delete('/delete_asset')
async def _(layer_name, user: User = Depends(current_user())):
    db_name = UserStoreInfo(user.nick_name).get_db_name()
    delete_feature_asset(layer_name, db_name)
    return BaseResponse(code=0, message='')


@router.post('/upload_raster')
async def _(file: UploadFile = File(...), user: User = Depends(current_user())):
    uploader = RasterGeo(user.nick_name)
    file_content = await file.read()
    await uploader.do_upload(layer_name=file.filename, file_content=file_content)
    return BaseResponse()
