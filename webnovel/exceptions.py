class NotSignedInException(Exception):
    """
    Raised when user not signed in to webnovel
    """

    def __init__(self, *args):
        super(NotSignedInException, self).__init__(*args)
