from .interface import BaseDecorator
from ..exceptions import NotSignedInException


class require_signin(BaseDecorator):
    """
    signed in checker decorator class
    """

    def __call__(self, *args, **kwargs):
        # if not bound to an object, raise value error
        if self.__self__ is None:
            raise ValueError

        if not self.__self__.is_signedin():
            raise NotSignedInException()

        return self.__wrapped__(self.__self__, *args, **kwargs)
