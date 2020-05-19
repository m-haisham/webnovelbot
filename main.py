import json
from pathlib import Path

from temp import THE_LORD_OF_MYSTERIES
from webnovel import WebnovelBot


def slugify(s):
    """
    Normalizes the string, converts to lowercase
    """
    return "".join(x if x.isalnum() else "_" for x in s).lower()


def scrape(bot, link):
    # OPTIONAL: if you want more chapters opened
    # webnovel.signin(USER_EMAIL, USER_PASS)

    ninfo = bot.novel(link)

    # create dir
    root = Path(ninfo['title'])
    root.mkdir(exist_ok=True, parents=True)

    # save info
    info_file = root / Path('_info.json')
    with info_file.open('w') as f:
        json.dump(ninfo, f)

    chapters = bot.table_of_contents()
    for chapter in chapters[list(chapters.keys())[0]][:10]:  # don't want all chapters scraped
        cinfo = bot.chapter(chapter)

        # write chapter
        chapter_file = root / Path(f'{slugify(cinfo["title"])}.json')
        with chapter_file.open('w') as f:
            json.dump(cinfo, f)


def claim_daily(bot):
    # webnovel.signin(USER_EMAIL, USER_PASS)

    # claim daily fast pass
    bot.power_vote()
    bot.claim_tasks()
    bot.energy_vote([1])


def show(coins, fastpass):
    for c in coins:
        c.ptype = 'coins'
    for c in fastpass:
        c.ptype = 'fastpass'

    a = sorted(coins + fastpass, key=lambda c: c.no)

    print('Chapters')
    print('--------')
    for c in a:
        print(f'no: {c.no}, title: {c.title}, cost: {c.cost}, type: {c.ptype}')

    print()
    print('    total cost')
    print('------------------')
    print(f'   coins: {sum([c.cost for c in coins])}')
    print(f'fastpass: {len(fastpass)}')


if __name__ == '__main__':
    webnovel = WebnovelBot(timeout=20)

    webnovel.driver.get(THE_LORD_OF_MYSTERIES)

    # webnovel.signin(USER_EMAIL, USER_PASS)

    profile = webnovel.profile()

    coins, fastpass = webnovel.batch_unlock(profile.coins, profile.fastpass, maximum_cost=10, execute=False)

    show(coins, fastpass)

    webnovel.close()
