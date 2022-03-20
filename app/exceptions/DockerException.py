from docker.errors import NotFound


class NotRunning(NotFound):
    pass
