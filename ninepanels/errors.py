class DatabaseConnectionError(Exception):
    """the database was not available"""

    pass


class UserNotCreated(Exception):
    pass

class UserNotFound(Exception):
    pass

class UserAlreadyExists(Exception):
    pass

class UserNotDeleted(Exception):
    pass

class EntryNotCreated(Exception):
    pass