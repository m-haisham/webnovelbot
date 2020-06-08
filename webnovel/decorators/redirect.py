import inspect

from .interface import MethodDecorator

URL_PARAM = 'url'


class redirect(MethodDecorator):
    def __call__(self, *args, **kwargs):
        super.__call__()

        url = None

        # check if url in kwargs
        if URL_PARAM in kwargs:
            url = kwargs[URL_PARAM]

        # check if url in args
        else:
            # get all args names of url
            # excluding the [self] arg
            args_names = inspect.getfullargspec(self.__wrapped__).args[1:]

            if URL_PARAM in args_names:
                # remove all parameters that are passed using kw
                # so args_names contains only those that haven't been passed as kw
                for kw in kwargs.keys():
                    args_names.remove(kw)

                index = args_names.index(URL_PARAM)
                try:
                    url = args[index]
                except IndexError:
                    pass

        if url is not None:
            self.__self__.driver.get(url)

        return self.__wrapped__(self.__self__, *args, **kwargs)
