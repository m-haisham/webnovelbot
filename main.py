import json
from pathlib import Path

from selenium.webdriver.common.action_chains import ActionChains

from temp import USER_PASS, USER_EMAIL, NOVEL
from webnovel import WebnovelBot
from webnovel.analytic import ForwardCrawl


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


def claim_daily(bot, novel=None):
    # webnovel.signin(USER_EMAIL, USER_PASS)

    # claim daily fast pass
    bot.power_vote()
    bot.claim_tasks()
    bot.energy_vote([1])

    if novel is not None:
        bot.driver.get(novel)


def show(analysis):
    for c in analysis.via_coins:
        c.ptype = 'coins'
    for c in analysis.via_fastpass:
        c.ptype = 'fastpass'

    a = sorted(analysis.via_coins + analysis.via_fastpass, key=lambda c: c.no)

    print('Chapters')
    print('--------')
    for c in a:
        print(f'no: {c.no}, title: {c.title.split(":")[0]}, cost: {c.cost}, type: {c.ptype}')

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

    analyser = ForwardCrawl(profile, maximum_cost=10, on_load=lambda c: focus(c))

    analysis = webnovel.batch_analyze(analyser, unlock=False)

    show(analysis)

    webnovel.close()
