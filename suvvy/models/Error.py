class AuthenticationError(BaseException):
    pass


class NotThatModel(BaseException):
    pass


class ModelLimitExceeded(BaseException):
    pass


class TokenNotFound(BaseException):
    pass