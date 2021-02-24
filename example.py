import sys

from selenium.webdriver.common.action_chains import ActionChains

from temp import NOVEL, USER_EMAIL, USER_PASS
from webnovel import WebnovelBot
from webnovel.analytic import Efficient
from webnovel.api import UnlockType
from webnovel.models import Novel


def slugify(s):
    """
    Normalizes the string, converts to lowercase
    """
    return "".join(x if x.isalnum() else "_" for x in s).lower()


def claim_daily(bot, novel=None):
    # claim daily fast pass
    bot.power_vote(novel)
    bot.claim_tasks()
    bot.energy_vote([1])


def format_title(s, l=20):
    if len(s) > l:
        return s[:l - 1] + '-'

    return s + (' ' * (l - len(s)))


def show(analysis):
    for c in analysis.via_coins:
        c.ptype = 'coins'
    for c in analysis.via_fastpass:
        c.ptype = 'fastpass'

    a = sorted(analysis.via_coins + analysis.via_fastpass, key=lambda c: c.no)

    print()
    print('Analysis report')
    print('---------------')
    for c in a:
        print(f'no: {c.no}, title: {format_title(c.title)}, cost: {c.cost}, type: {c.ptype}')

    print()
    print('total cost')
    print('----------')
    print(f'   coins: {analysis.coins_cost}')
    print(f'fastpass: {analysis.fastpass_cost}')


def focus(chapter):
    # get element
    selector = f"li[data-cid='{chapter.id}']"
    element = webnovel.driver.find_element_by_css_selector(selector)

    # move cursor
    ActionChains(webnovel.driver).move_to_element(element).perform()


def progress(c):
    print(f'no: {c.no}, title: {format_title(c.title)}, cost: {c.cost}')


if __name__ == '__main__':
    webnovel = WebnovelBot(timeout=360)

    webnovel.driver.get(NOVEL)
    novel_id = webnovel.novel_id

    # signin throws `ValueError` when the specified account cannot be found
    # / redirected to guard
    try:
        webnovel.signin(USER_EMAIL, USER_PASS)
    except ValueError:
        sys.exit(0)

    # claim_daily(webnovel, NOVEL)

    profile = webnovel.profile()

    api = webnovel.create_api()
    webnovel.close()

    # limit coin expenditure
    # profile.coins = min(profile.coins, 70)

    # analyser = ForwardCrawl(Novel(id=novel_id), profile, maximum_cost=10, on_load=progress)
    analyser = Efficient(Novel(id=novel_id), profile, on_load=progress)

    locked_chapters = [
        chapter
        for i, chapters in enumerate(api.toc(novel_id).values()) for chapter in chapters
        if chapter.locked
    ]

    print()
    print('Analysing')
    print('---------------')
    analysis = analyser.analyse(locked_chapters)

    show(analysis)

    try:
        input('\nRequesting permission to unlock chapters')
    except KeyboardInterrupt:
        print('Permission denied')

        import sys

        sys.exit()

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
