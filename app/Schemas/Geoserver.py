from typing import List, Any

from pydantic import BaseModel

from utils.constant.geo import GeoType, FieldType


class Field(BaseModel):
    field_name: str
    field_type: FieldType
    key: str


class CreateTable(BaseModel):
    layer_name: str
    geo_type: GeoType
    fields: List[Field] = []
