class NotSignedInException(Exception):
    """
    Raised when user not signed in to webnovel
    """

    def __init__(self, *args):
        super(NotSignedInException, self).__init__(*args)


class NotANovelUrlException(Exception):
    """
    Raised when the link is not a novel url
    """

    def __init__(self, *args):
        super(NotANovelUrlException, self).__init__(*args)


class ApiError(Exception):
    def __init__(self, *args):
        super(ApiError, self).__init__(*args)
