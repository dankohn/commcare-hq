
class RemoteRequestError(Exception):
    pass


class RemoteAuthError(RemoteRequestError):
    pass


class ActionNotPermitted(RemoteRequestError):
    pass
