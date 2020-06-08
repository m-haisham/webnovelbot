import functools
from copy import copy


class MethodDecorator:
    """
    __wrapped__: provides wrapped function
    __self__: provides wrapped functions class
    """

    def __init__(self, func):
        self.__self__ = None

        self.__wrapped__ = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        if self.__self__ is None:
            raise ValueError

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # create a bound copy
        bound = copy(self)
        bound.__self__ = instance

        # update __doc__ and similar attributes
        functools.update_wrapper(bound, self.__wrapped__)

        # add the bound instance to the object's dict so that
        # __get__ won't be called a 2nd time
        setattr(instance, self.__wrapped__.__name__, bound)

        return bound
