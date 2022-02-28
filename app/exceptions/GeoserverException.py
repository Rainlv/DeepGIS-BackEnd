class BaseGeoserverException(Exception):
    pass


class CreateFeatureStoreException(BaseGeoserverException):
    pass


class PublishFeatureException(BaseGeoserverException):
    pass


class CreateWorkspaceException(BaseGeoserverException):
    pass


class GetFeatureInfoException(BaseGeoserverException):
    pass


class DeleteWorkspaceException(BaseGeoserverException):
    pass

class DeleteFeatureStoreException(BaseGeoserverException):
    pass
