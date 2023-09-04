class DatabaseConnectionError(Exception):
    """the database was not available"""

    pass


class UserNotCreated(Exception):
    pass


class UserNotFound(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserNotUpdated(Exception):
    pass


class UserNotDeleted(Exception):
    pass


class EntryNotCreated(Exception):
    pass


class PanelNotCreated(Exception):
    pass


class PanelNotFound(Exception):
    pass


class PanelNotUpdated(Exception):
    pass


class PanelNotDeleted(Exception):
    pass


class EntriesNotDeleted(Exception):
    pass


class ConfigurationException(Exception):
    pass


class BlacklistedAccessTokenException(Exception):
    pass


class PasswordResetTokenException(Exception):
    pass

class WelcomeEmailException(Exception):
    pass
