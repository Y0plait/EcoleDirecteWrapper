class EdAPiExceptions(Exception):

    def __init__(self, msg=None, stacktrace=None):
        self.msg = msg
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = "%s\n" % self.msg

        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += "Stacktrace:\n%s" % stacktrace
        return exception_msg


class LoginRequired(EdAPiExceptions):
    """
    Thrown when user not logged in.
    """


class InvalidLogin(EdAPiExceptions):
    """
    Thrown when user's login are invalid/ incorrect.
    """

class ServerError(EdAPiExceptions):
    """
    Thrown when api returns an non-excepted error.
    """

class UnexistantPeriod(EdAPiExceptions):
    """
    Thrown when the period asked is not accesible.
    """