class BaseGeoserverException(Exception):
    pass


class CreateFeatureStoreException(BaseGeoserverException):
    pass


class FeatureStoreExistsException(CreateFeatureStoreException):
    pass


class PublishFeatureException(BaseGeoserverException):
    pass


class PublishRasterException(BaseGeoserverException):
    pass


class CreateWorkspaceException(BaseGeoserverException):
    pass


class WsExistException(CreateWorkspaceException):
    pass


class GetInfoException(BaseGeoserverException):
    pass


class DeleteWorkspaceException(BaseGeoserverException):
    pass


class DeleteFeatureStoreException(BaseGeoserverException):
    pass


class DeleteLayerException(BaseGeoserverException):
    pass


class NotExistStore(Exception):
    pass
