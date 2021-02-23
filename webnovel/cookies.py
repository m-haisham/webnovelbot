from typing import Optional, Iterable

import browser_cookie3
from requests.cookies import RequestsCookieJar


class Cookies(RequestsCookieJar):
    default_domains = (
        '.webnovel.com',
        'www.webnovel.com',
    )

    @classmethod
    def from_browser(cls, browser, domains: Optional[Iterable[str]] = None):
        """
        this function creates a Cookies object with the cookies from the given browser and the domains

        :param browser: browser from which to extract cookies
        :param domains: only cookies from these domains, when left empty uses `Cookies.default_domains`
        :raises TypeError: if the given browser is not supported
        :return: Cookies object containing the cookies
        """
        if domains is None:
            domains = cls.default_domains

        # check and see whether the expected browser is available
        try:
            func = getattr(browser_cookie3, browser)
        except AttributeError:
            raise TypeError(f'The provided browser ({browser}) is not supported')

        # create and fill the cookies jar
        cookiejar = Cookies()
        for domain in domains:
            for c in func(domain_name=domain):
                cookiejar.set(c.name, c.value, domain=c.domain, path=c.path)

        return cookiejar
