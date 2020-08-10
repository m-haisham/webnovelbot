import json
import re
from typing import List, Union, Dict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .analytic import IAnalyser, Analysis
from .api import ParsedApi, UnlockType
from .decorators import require_signin, redirect
from .exceptions import NotSignedInException, NotANovelUrlException
from .models import Profile, Novel, Chapter
from .tools import UrlTools

BASE_URL = 'https://www.webnovel.com'
EMAIL_LOGIN_URL = 'https://passport.webnovel.com/emaillogin.html'


class WebnovelBot:
    def __init__(self, driver: WebDriver = None, timeout=10):
        """
        :param driver: selenium web driver to use
        :param timeout: timeout for all class operations
        """
        if driver is None:
            self.driver = webdriver.Chrome()
        else:
            self.driver = driver
        self.timeout = timeout

    def create_api(self) -> ParsedApi:
        """
        :return: Api with cookies of the current selenium driver instance
        """
        return ParsedApi(self.driver.get_cookies())

    @property
    def novel_id(self):
        """
        get novel id from current url
        """
        url = self.driver.current_url
        if 'book' not in url:
            raise NotANovelUrlException

        return UrlTools.from_novel_url(url)

    @property
    def user_id(self):
        """
        :return: current user id
        """
        uid = self.driver.get_cookie('uid')

        # inline signing check
        if uid is None:
            raise NotSignedInException

        return int(uid['value'])

    def home(self):
        """
        load home
        """
        self.driver.get(BASE_URL)

    @require_signin
    def profile(self):
        """
        get profile information from popup

        :return: WebnovelProfile object
        """

        self._focus_profile()

        field_mapper = {
            'coins': 'Coins',
            'fastpass': 'Fast pass',
            'power_stone': 'Power Stones',
            'energy_stone': 'Energy Stones'
        }

        # redundancy check
        if list(field_mapper.keys()) != Profile.fields:
            raise ValueError('fields do not match')

        # generate dictionary using field_mapper as title value
        profile_data = {
            field: int(self.driver.find_element_by_css_selector(f"a[title='{value}'] > em").text)
            for field, value in field_mapper.items()
        }

        return Profile(id=self.user_id, **profile_data)

    def signin(self, email, password):
        """
        signin to webnovel using :param email: and :param password:
        """
        # go to login path
        self.driver.get(EMAIL_LOGIN_URL)

        self.driver.find_element_by_class_name('loginEmail').send_keys(email)
        self.driver.find_element_by_class_name('loginPass').send_keys(password)

        signin_btn = self.driver.find_element_by_id('submit')
        signin_btn.click()

        # wait till signin success
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='My Profile']"))
        )

    @require_signin
    def signout(self):
        # display the hover profile
        self._focus_profile()

        # click and out
        signout_button = self.driver.find_element_by_css_selector("a[class*='j_logout']")
        signout_button.click()

        # wait till logged out
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.login-btn'))
        )

    def is_signedin(self) -> bool:
        """
        checks for the existance of user id cookie

        :return: whether we are currently signed in
        """
        if self.driver.get_cookie('uid') is None:
            return False
        else:
            return True

    @require_signin
    def library(self, redirect: bool = True) -> List[Novel]:
        """
        :requires: to be signed in

        :return: all the novels in library
        """
        if redirect:
            self.driver.get(f'{BASE_URL}/library')

        # all novel containers
        novel_elements = self.driver.find_elements_by_css_selector('.lib-books > li')

        novels = []
        for element in novel_elements:
            link = element.find_element_by_css_selector('a')

            novel = Novel(
                title=link.text,
                url=link.get_attribute('href')
            )

            # this attribute does not exist in Novel class
            # ... it might be useful
            novel.update = '_update' in element.get_attribute('class')

            novels.append(novel)

        return novels

    @redirect
    def novel(self, url=None) -> Novel:
        """
        :param url: url to novel
        :return: Novel object
        """
        info_elems = self.driver.find_elements_by_css_selector('._mn > *')
        subinfo_elems = info_elems[1].find_elements_by_css_selector(':scope > *')
        writerinfo_elems = info_elems[2].find_elements_by_css_selector('p > *')

        novel = Novel()

        novel.id = self.driver.current_url.split('/')[4]
        novel.title = info_elems[0].text[:-len(info_elems[0].find_element_by_tag_name('small').text) - 1],
        novel.title = novel.title[0]

        novel.synopsis = self.driver.find_element_by_css_selector("div[class*='j_synopsis'] > p").text
        novel.genre = subinfo_elems[0].text,
        novel.views = subinfo_elems[-1].text[:-6],
        novel.url = self.driver.current_url
        novel.cover_url = f'https://img.webnovel.com/bookcover/{novel.id}'

        # ratings are posted up to 5, they are converted to float and normalized to 1
        novel.rating = float(info_elems[3].find_element_by_css_selector('strong').text) / 5.0,

        # stripped of all non numerals and converted to int
        novel.review_count = int(
            info_elems[3].find_element_by_css_selector('small').text.strip('()')[:-8].replace(',', ''))

        # writer info
        for i in range(round(len(writerinfo_elems) / 2)):
            label = writerinfo_elems[i * 2].text.strip(':').lower()
            value = writerinfo_elems[i * 2 + 1].text

            setattr(novel, label, value)

        return novel

    def table_of_contents(self) -> Dict[str, List[Chapter]]:
        """
        Must be used while a particular novel is loaded to driver

        :return: dict of volumes in order, where key is volume name and value the chapters
        """

        # load table of contents
        table_of_contents = self.driver.find_element_by_css_selector('a.j_show_contents')
        table_of_contents.click()

        # wait until table of contents loads
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'volume-item'))
        )

        # using bs4 to parse
        # bs4 is faster than selenium selectors
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        volume_elements = soup.find_all('div', {'class': 'volume-item'})
        volumes = {}
        for volume_element in volume_elements:
            volume_chapters = volume_element.find_all('li', {'class': 'g_col_6'})

            chapters = []
            for chapter in volume_chapters:
                no_element = chapter.select_one('a > i')

                chapter = Chapter(
                    title=chapter.select_one('a')['title'],
                    url=f"http:{chapter.find('a')['href'].strip()}",
                    locked=bool(chapter.select('a > svg'))
                )

                if no_element is not None:
                    chapter.no = int(no_element.text.strip())
                else:
                    chapter.no = 0

                chapter.id = chapter.chapter_id_from_url()

                chapters.append(chapter)

            _name = volume_element.find('h4').text
            volume_name = re.sub(r'\n +', '', _name).replace(':', ': ')
            volumes[volume_name] = chapters

        return volumes

    @redirect
    def chapter(self, url=None, is_locked=False) -> Chapter:
        """
        :param url: url to chapter
        :param is_locked: whether the chapter is locked
        :return: Chapter object
        """
        # wait till chapter loads
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cha-tit'))
        )

        # if locked, ensure lock element loads
        # lock element may take some time to load
        if is_locked:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.j_locked_chap'))
            )

        chapter = Chapter(
            no=int(self.driver.find_element_by_css_selector('.j_chapIdx').text.strip('Chapter ')[:-1]),
            url=self.driver.current_url,
            title=self.driver.find_element_by_css_selector('.cha-tit').find_element_by_tag_name('h3').text,
            locked=self.is_chapter_locked(),
        )

        if chapter.locked:
            if self.is_signedin():
                unlock_params = self.driver.find_element_by_css_selector(
                    "div[class*='lock-group j_lock_btns '] > a[class*='j_unlockChapter']"
                ).get_attribute('data-unlock-params')
            else:
                unlock_params = self.driver.find_element_by_css_selector(
                    "div[class*='lock-group j_lock_btns '] > a[class*='_bt_unlock']"
                ).get_attribute('data-unlock-params')

            chapter.cost = json.loads(unlock_params)['chapterPrice']
        else:
            chapter.paragraphs = [wrapper.text
                                  for wrapper in self.driver.find_elements_by_css_selector('.cha-paragraph > span > p')]

        return chapter

    @redirect
    def is_chapter_locked(self, url=None):
        return bool(self.driver.find_elements_by_css_selector('.j_locked_chap'))

    def unlock_chapter(self, url=None, coins=False, fastpass=False, unlock_delay=2):
        """
        unlocks the chapter using either coins or fastpass

        either one of [coins] and [fastpass] must be true
        if both options are available, [coins] are given priority

        :required: to be signed in

        :param url: url to chapter
        :param coins: use coins to unlock
        :param fastpass: use fastpass to unlock
        :param unlock_delay: delay between mouse moving to unlock button to clicking.
                             this is introduced as unlock can fail due to some latency issues
        """
        # error testing parameters
        if not coins and not fastpass:
            raise ValueError('Choose atleast one from "coins" or "fastpass"')

        # manual [url] and [signin] check
        # as [coins] and [fastpass] check needs priority
        if url is not None:
            self.driver.get(url)

        # sign in check
        if not self.is_signedin():
            raise NotSignedInException()

        # wait till lock element loads
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.j_locked_chap'))
        )

        # check which options are available [coins, fastpass]
        # coins
        try:
            can_coin = True
            self.driver.find_element_by_css_selector("div[class='lock-group j_lock_btns ']")
        except NoSuchElementException:
            can_coin = False

        # fastpass
        try:
            can_fastpass = True
            self.driver.find_element_by_css_selector("div[class^='lock-foot'] > div:nth-child(2) > a")
        except NoSuchElementException:
            can_fastpass = False

        def unlock(button):
            """
            :param button: button to click to unlock
            """
            ActionChains(self.driver).move_to_element(button).pause(unlock_delay).click().perform()

        if coins and can_coin:
            coin_button = self.driver.find_element_by_css_selector(
                "div[class='lock-group j_lock_btns '] > a[class*='j_unlockChapter']")
            unlock(coin_button)

        elif fastpass and can_fastpass:
            fastpass_button = self.driver.find_element_by_css_selector("div[class^='lock-foot'] > div:nth-child(2) > a")
            unlock(fastpass_button)

    def batch_unlock(self, analysis, selenium=False):
        """
        unlocks all the chapters in analysis according to assortment
        Uses api to do post requests by default

        :require: to be signed in

        :param selenium: [Outdated] whether to use selenium to unlock, default is [False]
        :param analysis: object to denote which to unlock in which
        :return: None
        """
        if selenium:
            # [outdated]
            # signed in check not in method
            # as mainly consisting of [unlock_chapter] which has signin check
            for c in analysis.via_coins:
                self.unlock_chapter(c.url, coins=True)
            for c in analysis.via_fastpass:
                self.unlock_chapter(c.url, fastpass=True)

        else:
            api = self.create_api()
            for c in analysis.via_coins:
                api.unlock(c.novel_id_from_url(), c, UnlockType.coins)
            for c in analysis.via_fastpass:
                api.unlock(c.novel_id_from_url(), c, UnlockType.fastpass)

    @redirect
    def batch_analyze(self, analyser: IAnalyser, url=None) -> Analysis:
        """
        batch unlocks chapters in ascending order

        :require: to be signed in

        :param analyser: analyser for chapters to unlock
        :param url: url to novel
        :return: list of unlocked chapters
        """
        # get all locked chapters
        locked_chapters = [chapter for chapters in self.table_of_contents().values() for chapter in chapters]

        return analyser.analyse(locked_chapters)

    @require_signin
    def energy_vote(self, votes: Union[int, List[int]], lead='male', redirect=True):
        """
        votes for the selected indexes of the queue of stories to be released

        :requires: to be signed in

        :param votes: number of votes to cast or indexes of stories in queue to vote
        :param lead: either 'male' or 'female' options, to specify which list to select
        :param redirect: whether to load the vote page again
        """

        # to energy_vote screen
        if redirect:
            self.driver.get(f'{BASE_URL}/vote')

        # set indexes to be unlocked
        indexes = None
        if type(votes) == list:
            indexes = votes
        elif type(votes) == int:
            indexes = range(votes)

        vote_buttons = [tile.find_element_by_css_selector('._voteBtn')
                        for tile
                        in self.driver.find_elements_by_css_selector(f'#List{lead.capitalize()} > *')]

        for i in indexes:
            vote_buttons[i].click()

    @require_signin
    def claim_tasks(self):
        """
        collects all completed task rewards

        :requires: to be signed in
        """
        # hover over profile button to reveal show claim_tasks button
        self._focus_profile()

        # click to show claim_tasks
        show_tasks = self.driver.find_element_by_css_selector('.j_show_task_mod')
        show_tasks.click()

        # wait till taska loaded
        WebDriverWait(self.driver, timeout=self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.j_daily_task'))
        )

        # claim all rewards
        for claim in self.driver.find_elements_by_css_selector('.j_claim_task'):
            claim.click()

        # exit
        exit_button = self.driver.find_element_by_css_selector("#taskMod > div > a[class='_close']")
        exit_button.click()

        # wait till popup closes
        WebDriverWait(self.driver, self.timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[id='taskMod'][class*='_on']"))
        )

    @require_signin
    def power_vote(self, url: str = None, repeat: int = 1):
        """
        energy_vote with power stone to [url]

        :requires: to be signed in

        :param url: url of novel to power up, if this is not specified tries to energy_vote in current page

        :param repeat: number of times to press button.
        :default repeat: 1
        """
        if url is not None:
            self.driver.get(url)

        # get power stone energy_vote button
        power_button = self.driver.find_element_by_css_selector(".j_power_btn_area > .j_vote_power")

        for _ in range(repeat):
            power_button.click()

    def close(self):
        self.driver.close()

    def _focus_profile(self):
        """
        moves mouse over to profile button

        :return: profile button element
        """
        profile_button = self.driver.find_element_by_css_selector("div[class^='g_user'][class*='_hover']")
        ActionChains(self.driver).move_to_element(profile_button).perform()

        return profile_button
