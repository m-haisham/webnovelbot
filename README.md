# Webnovel Bot

Webnovel Bot and scraper written in one, optimized for speed.

Provides multiple choices of access for tasks

## Install

```
pip install webnovelbot
```

## Sample

```python
webnovel = WebnovelBot(timeout=360)

webnovel.driver.get(NOVEL)

# get the novel id of current loaded novel
novel_id = webnovel.novel_id

webnovel.signin(USER_EMAIL, USER_PASS)

# claim_daily(webnovel, NOVEL)

profile = webnovel.profile()

api = webnovel.create_api()
webnovel.close()

# limit coin expenditure
# profile.coins = min(profile.coins, 70)

# on_load is called after each response to request
# may be used to cache the requests
analyser = ForwardCrawl(Novel(id=novel_id), profile, maximum_cost=10, on_load=progress)

locked_chapters = [
    chapter
    for i, chapters in enumerate(api.toc(novel_id).values()) for chapter in chapters
    if chapter.no > 160 and chapter.locked
]

print()
print('Analysing')
print('---------------')
analysis = analyser.analyse(locked_chapters)

print()
print('Unlocking')
print('---------')
for c in analysis.via_coins:
    print(f'no: {c.no}, title: {format_title(c.title)}, cost: {c.cost}, type: coins ... ', end='')
    api.unlock(c.novel_id_from_url(), c, UnlockType.coins)
    print('unlocked')
for c in analysis.via_fastpass:
    print(f'no: {c.no}, title: {format_title(c.title)}, cost: {c.cost}, type: fastpass ... ', end='')
    api.unlock(c.novel_id_from_url(), c, UnlockType.fastpass)
    print('unlocked')
```

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

Selenium is currently mainly being used to get access tokens.
