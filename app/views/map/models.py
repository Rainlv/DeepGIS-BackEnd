from typing import List
from pydantic import BaseModel
from utils.constant.geo import GeoType, FieldType
from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry


class Field(BaseModel):
    field_name: str
    field_type: FieldType
    key: str


class CreateTable(BaseModel):
    layer_name: str
    geo_type: GeoType
    fields: List[Field] = []


class BasePointModel:
    FID = Column("FID", Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))


class BasePolygonModel:
    FID = Column("FID", Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))


class BaseLineModel:
    FID = Column("FID", Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='LINESTRING', srid=4326))
