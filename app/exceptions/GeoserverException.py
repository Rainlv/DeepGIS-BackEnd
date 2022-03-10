class BaseGeoserverException(Exception):
    pass


class CreateFeatureStoreException(BaseGeoserverException):
    pass


class PublishFeatureException(BaseGeoserverException):
    pass


class PublishRasterException(BaseGeoserverException):
    pass


class CreateWorkspaceException(BaseGeoserverException):
    pass


class GetInfoException(BaseGeoserverException):
    pass


class DeleteWorkspaceException(BaseGeoserverException):
    pass


class DeleteFeatureStoreException(BaseGeoserverException):
    pass


class DeleteLayerException(BaseGeoserverException):
    pass
