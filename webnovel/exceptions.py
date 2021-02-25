class NotSignedInException(Exception):
    """
    Raised when user not signed in to webnovel
    """
    pass


class NotANovelUrlException(Exception):
    """
    Raised when the link is not a novel url
    """
    pass


class ApiError(Exception):
    pass


class GuardException(Exception):
    pass


class CaptchaException(Exception):
    pass


class ValidationError(Exception):
    pass
