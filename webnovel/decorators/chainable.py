from functools import wraps


def chainable(func):
    """
    enables chaining of methods

    this makes the return of the function to be the class or `self`

    example usage:

        @chainable
        def a_class_method(self):
            ...

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

        # when used with a method, the first arg is always the class
        return args[0]

    return wrapper
