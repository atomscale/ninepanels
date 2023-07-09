class DatabaseConnectionError(Exception):
    """the database was not available"""

    pass


class UserNotCreated(Exception):
    pass