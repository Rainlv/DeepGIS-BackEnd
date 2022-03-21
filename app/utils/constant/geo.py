from enum import Enum


# *``"GEOMETRY"``,
# *``"POINT"``,
# *``"LINESTRING"``,
# *``"POLYGON"``,
# *``"MULTIPOINT"``,
# *``"MULTILINESTRING"``,
# *``"MULTIPOLYGON"``,
# *``"GEOMETRYCOLLECTION"``,
# *``"CURVE"``,
# *``None``.
class GeoType(str, Enum):
    POINT = "POINT"
    Line = "LINESTRING"
    POLYGON = "POLYGON"
    MULTIPOINT = "MULTIPOINT"
    MULTILINESTRING = "MULTILINESTRING"
    MULTIPOLYGON = "MULTIPOLYGON"


class FieldType(str, Enum):
    INT = "Integer"
    FLOAT = "Float"
    STRING = "String"
    DATETIME = "DateTime"


class WorkspaceType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SHARE = "share"


class LayerType(str, Enum):
    RASTER = "raster"
    FEATURE = "feature"


class StoreType(str, Enum):
    Private = "private"
    Public = "public"
    Share = "share"
