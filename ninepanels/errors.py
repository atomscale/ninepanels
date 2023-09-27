import logging
from .pydmodels import LogMessage


class NinePanelsBaseException(Exception):

    """Base exception for all custom exceptions.
    Standardises logging schema and behaviours for exceptions
    using the .pydmodels.LogMessage model.

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
        if detail:
            self.detail = detail
        else:
            self.detail = self.__class__.__name__

        super().__init__(self.detail)

        log_message = LogMessage(
            detail=self.detail,
            level="error",
            context_msg=context_msg,
            context_data=context_data,
        )

        logging.error(log_message.model_dump())
        # TODO this is where push to the async db write call feature will happen


class DatabaseConnectionError(NinePanelsBaseException):
    pass


class UserNotCreated(NinePanelsBaseException):
    pass


class UserNotFound(NinePanelsBaseException):
    pass


class UserNotUpdated(NinePanelsBaseException):
    pass


class UserNotDeleted(NinePanelsBaseException):
    pass


class EntryNotCreated(NinePanelsBaseException):
    pass


class PanelNotCreated(NinePanelsBaseException):
    pass


class PanelNotFound(NinePanelsBaseException):
    pass


class PanelNotUpdated(NinePanelsBaseException):
    pass


class PanelNotDeleted(NinePanelsBaseException):
    pass


class PanelsNotSorted(NinePanelsBaseException):
    pass


class EntriesNotDeleted(NinePanelsBaseException):
    pass


class ConfigurationException(NinePanelsBaseException):
    pass


class BlacklistedAccessTokenException(NinePanelsBaseException):
    pass


class PasswordResetTokenException(NinePanelsBaseException):
    pass


class EmailException(NinePanelsBaseException):
    pass


class MonitorError(NinePanelsBaseException):
    pass
