from fastapi import APIRouter, Depends
from Schemas.Geoserver import CreateTable
from Schemas.Response import BaseResponse
from views.map.db import create_geo_table
from sqlalchemy import Column
import sqlalchemy
from views.map.geoserver import geoserver as geoserver_instance
from views.user.models import User
from views.user.users import current_user

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
    geoserver_instance.pub_feature(feature_name=table_name, feature_store=user_name, ws=user_name)
    return BaseResponse(
        code=0,
        message=""
    )


@router.get("/get_user_features")
async def _(user: User = Depends(current_user())):
    user_name = user.nick_name
    public_raster = 'nurc'
    public_feature = 'tiger'
    user_feature_result = geoserver_instance.get_ws_features(user_name)
    public_feature_result = geoserver_instance.get_ws_features(public_feature)
    share_feature_result = geoserver_instance.get_ws_features('share')
    user_raster_result = []
    public_raster_result = geoserver_instance.get_ws_features(public_raster)
    share_raster_result = geoserver_instance.get_ws_features('share')
    return BaseResponse(
        code=0,
        message='',
        result=[
            {"id": "user", "label": "我的资源",
             "children": [
                 {
                     "id": "user_feature", "label": "矢量数据",
                     "children": [
                         {"id": f"{user_name}:{feature_name}", "label": feature_name, "type": "feature"}
                         for feature_name in user_feature_result]
                 },
                 {
                     "id": "user_raster", "label": "栅格数据",
                     "children": [
                         {"id": f"{user_name}:{raster_name}", "label": raster_name, "type": "raster"}
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
