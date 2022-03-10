from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException
from starlette.responses import FileResponse

from Schemas.Geoserver import CreateTable
from Schemas.Response import BaseResponse
from utils.constant.geo import LayerType, StoreType
from utils.geoserver import get_user_store_name, get_raster_path
from views.map.db import create_geo_table, upload2postGIS, download_from_postGIS, delete_feature_asset, RasterPostGIS
from sqlalchemy import Column
import sqlalchemy
from views.map.geoserver import geoserver as geoserver_instance
from views.user.models import User
from views.user.users import current_user
from fastapi.responses import StreamingResponse

router = APIRouter(tags=['geoserver'], prefix="/geoserver")


@router.post("/create_table")
async def _(param: CreateTable, user: User = Depends(current_user())):
    user_name = user.nick_name
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
    create_geo_table(db_name=user_name, table_name=table_name, geo_type=geo_type, fields=field_cols)
    geoserver_instance.pub_feature(feature_table_name=table_name, feature_store=user_name, ws=user_name)
    return BaseResponse(
        code=0,
        message=""
    )


@router.get("/get_user_features")
async def _(user: User = Depends(current_user())):
    user_name = user.nick_name
    user_feature = get_user_store_name(user_name, layer_type=LayerType.FEATURE)
    user_raster = get_user_store_name(user_name, layer_type=LayerType.RASTER)
    public_raster = 'nurc'
    public_feature = 'tiger'
    user_feature_result = geoserver_instance.get_ws_layers(user_feature)
    public_feature_result = geoserver_instance.get_ws_layers(public_feature)
    share_feature_result = geoserver_instance.get_ws_layers('share')
    user_raster_result = geoserver_instance.get_ws_layers(user_raster)
    public_raster_result = geoserver_instance.get_ws_layers(public_raster)
    share_raster_result = geoserver_instance.get_ws_layers('share')
    return BaseResponse(
        code=0,
        message='',
        result=[
            {"id": "user", "label": "我的资源",
             "children": [
                 {
                     "id": "user_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"{user_feature}:{feature_name}", "label": feature_name, "type": "feature"}
                         for feature_name in user_feature_result]
                 },
                 {
                     "id": "user_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"{user_raster}:{raster_name}", "label": raster_name, "type": "raster"}
                         for raster_name in user_raster_result]},
             ]},
            {"id": "public", "label": "公共资源",
             "children": [
                 {
                     "id": "public_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"{public_feature}:{feature_name}",
                          "label": feature_name, "type": "feature"}
                         for feature_name in public_feature_result]},
                 {
                     "id": "public_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"{public_raster}:{raster_name}", "label": raster_name, "type": "raster"}
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
    db_name = get_user_store_name(user.nick_name, layer_type=LayerType.FEATURE)
    upload2postGIS(file.file, filename=file.filename, db_name=db_name)
    return BaseResponse(
        code=0,
        message='',
    )


# TODO: 公共数据库和共享库支持，多文件类型支持
@router.get('/download_features')
async def _(feature_name: str, store_type: StoreType = StoreType.Private,
            user: User = Depends(current_user())):
    db_name = get_user_store_name(user.nick_name, layer_type=LayerType.FEATURE)
    content = download_from_postGIS(feature_name, db_name=db_name, out_file_type='GeoJSON')
    headers = {"Access-Control-Expose-Headers": "content-disposition",
               'content-disposition': f'attachment;filename={feature_name}.geojson',
               "content-type": 'application/octet-stream'}
    return StreamingResponse(content, headers=headers)


@router.delete('/delete_asset')
async def _(layer_name, layer_type: LayerType, user: User = Depends(current_user())):
    db_name = get_user_store_name(user.nick_name, layer_type=LayerType.FEATURE)
    delete_feature_asset(layer_name, db_name)
    return BaseResponse(code=0, message='')


@router.post('/upload_raster')
async def _(file: UploadFile = File(...), user: User = Depends(current_user())):
    uploader = RasterPostGIS(user.nick_name)
    file_content = await file.read()
    await uploader.do_upload(filename=file.filename, file_content=file_content)


# TODO: 公共数据库和共享库支持，多文件类型支持
@router.get('/download_raster')
async def _(raster_name: str, file_type: str = None, store_type: StoreType = StoreType.Private,
            user: User = Depends(current_user())):
    user_name = user.nick_name
    asset_dir = get_raster_path(user_name)
    file_path = Path(asset_dir).joinpath(raster_name)
    return FileResponse(path=file_path)
