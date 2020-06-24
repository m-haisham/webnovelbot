# Webnovel Bot

Webnovel Bot written in python using selenium.

## Features

* Sign in.
* Read profile information.
* Read Novel information.
* Vote using Power stones.
* Vote using Energy stones.
* Read table of contents.
* Scrape chapters, only unlocked.
* Unlock chapters by spending either coins or fastpass.
* Batch unlock chapters efficiently.
* Claim task rewards, including daily login rewards.

## Sample

```python
webnovel = WebnovelBot(timeout=20)

# webdriver can be accessed as .driver
webnovel.driver.get(NOVEL)

webnovel.signin(USER_EMAIL, USER_PASS)

webnovel.power_vote()
webnovel.claim_tasks()
webnovel.energy_vote([1])

# get profile info
profile = webnovel.profile()

# pick an analysis option
analyser = ForwardCrawl(Novel(id=webnovel.novel_id), profile, maximum_cost=10)
# analyser = Efficient(Novel(id=webnovel.novel_id), profile)

# gives chapters to unlock and using which [coins / fastpass]
analysis = webnovel.batch_analyze(analyser)

# or use a for loop
webnovel.batch_unlock(analysis)

webnovel.close()
```

## Analysers

### Forward Crawl

Calculate while abiding by the rules:

 - all chapters must be unlocked continuously
 - cheaper chapters with coins
 - expensive chapters with fastpass
 - chapters unlocked using coins must not exceed `maximum_cost` individually
 
### Efficient

The only difference between [Forward Crawl](#forward-crawl) and **Efficient**
is that the unlocked chapters wont be continuous

### HardLine

Takes a hard stance and draws two lines. One for coins and another fastpass.

Anything below or equal to coins line is selected for coins. And 
anything above or equal to fastpass line is selected for fastpass

That is until provided profile resources are exhausted.

