# Webnovel Bot

Webnovel Bot and scraper written in one, optimized for speed.

Provides multiple choices of access for tasks

## Install

```bash
pip install webnovelbot
```

or

```bash
pip install git+https://github.com/mHaisham/webnovelbot.git
```

## [Sample][1]

follow the [link][1] for an example usage

[1]: https://github.com/mHaisham/webnovelbot/blob/master/example.py

## Cookies

Webnovelbot supports using cookies from other web browsers in both selenium and api using class `Cookies`

It currently supports all browsers supported by [browser_cookie3](https://github.com/borisbabic/browser_cookie3)

`chrome` `firefox` `opera` `edge` `chromium`

```python
from webnovel import WebnovelBot, Cookies
from webnovel.api import ParsedApi

webnovel = WebnovelBot(timeout=360)

cookiejar = Cookies.from_browser('chrome')

# this will load the cookie jar into selenium
# depending on what you want to do after, you may want to reload the page
webnovel.add_cookiejar(cookiejar)

# this will create the api with the cookie jar
api = ParsedApi(cookiejar)
```

`Cookies` extends from `RequestsCookieJar` hence can be used as a replacement for it and vice-versa

## Conversion tools

```python
from webnovel.tools import UrlTools
```

UrlTools provides methods to convert and from `novel_id`, `chapter_id`, and `profile_id` to their respective urls

## Analytics

Supports multiple analytic tools with an easily extensible interface

[Read more](https://github.com/mHaisham/webnovelbot/tree/master/webnovel/analytic)

## Goals

Primary focus of development is to reduce the usage of selenium.
