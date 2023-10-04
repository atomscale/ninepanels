class NinePanelsBaseException(Exception):

    """Base exception for all custom exceptions.

    Args:
        detail: user friendly message that may make it to the
                front end (aligns with HTTPException's `detail` arg).
                Defaults to the name of the class if omitted. Please do not omit unless
                absolutely necessary.
        context_msg: space for a techincally detailed message
        context_data: kwargs to accept additonal key=value pairs of contextual data

    Returns: None
    Raises: None
    """

    def __init__(
        self, detail: str = None, context_msg: str = None, **context_data: dict
    ):
        self.detail = detail
        self.context_msg = (context_msg,)
        self.context_data = context_data


class DatabaseConnectionError(NinePanelsBaseException):
    ...


class UserNotCreated(NinePanelsBaseException):
    ...


class UserNotFound(NinePanelsBaseException):
    ...


class UserNotUpdated(NinePanelsBaseException):
    ...


class UserNotDeleted(NinePanelsBaseException):
    ...


class IncorrectPassword(NinePanelsBaseException):
    ...


class AccessTokenError(NinePanelsBaseException):
    ...


class EntryNotCreated(NinePanelsBaseException):
    ...


class PanelNotCreated(NinePanelsBaseException):
    ...


class PanelNotFound(NinePanelsBaseException):
    ...


class PanelNotUpdated(NinePanelsBaseException):
    ...


class PanelNotDeleted(NinePanelsBaseException):
    ...


class PanelsNotSorted(NinePanelsBaseException):
    ...


class EntriesNotDeleted(NinePanelsBaseException):
    ...


class ConfigurationException(NinePanelsBaseException):
    ...


class BlacklistedAccessTokenException(NinePanelsBaseException):
    ...


class PasswordResetTokenException(NinePanelsBaseException):
    ...


class EmailException(NinePanelsBaseException):
    ...


class RouteTimerError(NinePanelsBaseException):
    ...

class RouteStatsProcessorError(NinePanelsBaseException):
    ...

class ParseSortBy(NinePanelsBaseException):
    ...