class NotSignedInError(Exception):
    def __init__(self, *args):
        super(NotSignedInError, self).__init__(*args)
