from .interface import MethodDecorator
from ..exceptions import NotSignedInException


class require_signin(MethodDecorator):
    """
    signed in checker decorator class
    """

    def __call__(self, *args, **kwargs):
        super.__call__()

        if not self.__self__.is_signedin():
            raise NotSignedInException()

        return self.__wrapped__(self.__self__, *args, **kwargs)
