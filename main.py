from selenium.webdriver.common.action_chains import ActionChains

from temp import NOVEL, USER_EMAIL, USER_PASS
from webnovel import WebnovelBot
from webnovel.analytic import Efficient
from webnovel.models import Novel


def slugify(s):
    """
    Normalizes the string, converts to lowercase
    """
    return "".join(x if x.isalnum() else "_" for x in s).lower()


def claim_daily(bot, novel=None):
    # claim daily fast pass
    bot.power_vote()
    bot.claim_tasks()
    bot.energy_vote([1])

    import time
    time.sleep(5)

    if novel is not None:
        bot.driver.get(novel)


def show(analysis):
    for c in analysis.via_coins:
        c.ptype = 'coins'
    for c in analysis.via_fastpass:
        c.ptype = 'fastpass'

    a = sorted(analysis.via_coins + analysis.via_fastpass, key=lambda c: c.no)

    def format_title(s, l=20):
        if len(s) > l:
            return s[:l - 1] + '-'

        return s + (' ' * (l - len(s)))

    print('Chapters')
    print('--------')
    for c in a:
        print(f'no: {c.no}, title: {format_title(c.title)}, cost: {c.cost}, type: {c.ptype}')

    print()
    print('    total cost')
    print('------------------')
    print(f'   coins: {analysis.coins_cost}')
    print(f'fastpass: {analysis.fastpass_cost}')


def focus(chapter):
    # get element
    selector = f"li[data-cid='{chapter.id}']"
    element = webnovel.driver.find_element_by_css_selector(selector)

    # move cursor
    ActionChains(webnovel.driver).move_to_element(element).perform()


if __name__ == '__main__':
    webnovel = WebnovelBot(timeout=20)

    webnovel.driver.get(NOVEL)

    webnovel.signin(USER_EMAIL, USER_PASS)

    # claim_daily(webnovel, NOVEL)

    profile = webnovel.profile()
    # profile = Profile(coins=55, fastpass=6)

    # analyser = ForwardCrawl(Novel(id=webnovel.novel_id), profile, maximum_cost=10, on_load=lambda c: focus(c))
    analyser = Efficient(Novel(id=webnovel.novel_id), profile, on_load=lambda c: focus(c))

    analysis = webnovel.batch_analyze(analyser)

    show(analysis)

    webnovel.batch_unlock(analysis)

    webnovel.close()
