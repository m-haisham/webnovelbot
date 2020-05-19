import functools
import json
import math
from copy import copy
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .chapter import Chapter
from .exceptions import NotSignedInError
from .profile import WebnovelProfile

BASE_URL = 'https://www.webnovel.com'


class WebnovelBot:
    class require_signin(object):
        """
        signed in checker decorator class
        """

        def __init__(self, func):
            self.__self__ = None

            self.__wrapped__ = func
            functools.update_wrapper(self, func)

        def __call__(self, *args, **kwargs):
            # if not bound to an object, raise value error
            if self.__self__ is None:
                raise ValueError

            if not self.__self__.is_signedin():
                raise NotSignedInError()

            return self.__wrapped__(self.__self__, *args, **kwargs)

        def __get__(self, instance, owner):
            if instance is None:
                return self

            # create a bound copy
            bound = copy(self)
            bound.__self__ = instance

            # update __doc__ and similar attributes
            functools.update_wrapper(bound, self.__wrapped__)

            # add the bound instance to the object's dict so that
            # __get__ won't be called a 2nd time
            setattr(instance, self.__wrapped__.__name__, bound)

            return bound

    def __init__(self, timeout=10):
        self.driver = webdriver.Chrome()
        self.timeout = timeout

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
        if list(field_mapper.keys()) != WebnovelProfile.fields:
            raise ValueError('fields do not match')

        # generate dictionary using field_mapper as title value
        profile_data = {
            field: int(self.driver.find_element_by_css_selector(f"a[title='{value}'] > em").text)
            for field, value in field_mapper.items()
        }

        return WebnovelProfile(**profile_data)

    def signin(self, email, password):
        """
        signin to webnovel using :param email: and :param password:
        """

        # open signin frame
        login_btn = self.driver.find_element_by_css_selector('.login-btn')
        login_btn.click()

        # switch to signin frame
        self.driver.switch_to.frame('frameLG')

        # wait till signin buttons loaded
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'm-login-bts'))
        )

        # go to signin by email
        login_email = self.driver.find_element_by_css_selector("a[title='Log in with Email']")
        login_email.click()

        self.driver.find_element_by_class_name('loginEmail').send_keys(email)
        self.driver.find_element_by_class_name('loginPass').send_keys(password)

        signin_btn = self.driver.find_element_by_id('submit')
        signin_btn.click()

        # switch back to default frame
        self.driver.switch_to.default_content()

        # wait till signin success
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='My Profile']"))
        )

    def is_signedin(self):
        """
        :return: whether we are currently signed in
        """
        try:
            self.driver.find_element_by_css_selector("a[title='My Profile']")
        except NoSuchElementException:
            return False

        return True

    def novel(self, url):
        """
        :param url: url to novel
        :return: info about novel { title, genre, views, rating, review_count, author, translator[Conditional],
                                    editor[Conditional] }
        """
        self.driver.get(url)

        info_elems = self.driver.find_elements_by_css_selector('._mn > *')
        subinfo_elems = info_elems[1].find_elements_by_css_selector(':scope > *')
        writerinfo_elems = info_elems[2].find_elements_by_css_selector('p > *')

        info = {
            'title': info_elems[0].text[:-len(info_elems[0].find_element_by_tag_name('small').text) - 1],
            'genre': subinfo_elems[0].text,
            'views': subinfo_elems[3].text[:-6],

            # ratings are posted up to 5, they are converted to float and normalized to 1
            'rating': float(info_elems[3].find_element_by_css_selector('strong').text) / 5.0,

            # stripped of all non numerals and converted to int
            'review_count': int(
                info_elems[3].find_element_by_css_selector('small').text.strip('()')[:-8].replace(',', ''))
        }

        # writer info
        for i in range(round(len(writerinfo_elems) / 2)):
            label = writerinfo_elems[i * 2].text.strip(':').lower()
            value = writerinfo_elems[i * 2 + 1].text

            info[label] = value

        return info

    def table_of_contents(self):
        """
        Must be used while a particular novel is loaded to driver

        :return: Chapter object with attributes [no, url, locked]
        """

        # load table of contents
        table_of_contents = self.driver.find_element_by_css_selector("a[href='#contents']")
        table_of_contents.click()

        # wait until table of contents loads
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'volume-item'))
        )

        # using bs4 to parse
        # bs4 is faster than selenium selectors
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        volumes = soup.find_all('div', {'class': 'volume-item'})
        chapters = {}
        for volume in volumes:
            volume_title = volume.find('h4').text.strip()
            volume_chapters = volume.find_all('li', {'class': 'g_col_6'})

            chapters[volume_title] = [
                Chapter(
                    no=int(chapter.select_one('a > i').text.strip()),
                    url=f"http:{chapter.find('a')['href'].strip()}",
                    locked=bool(chapter.select('a > svg'))
                ) for chapter in volume_chapters
            ]

        return chapters

    def chapter(self, url, is_locked=False) -> Chapter:
        """
        :param url: url to chapter
        :param is_locked: whether the chapter is locked
        :return: Chapter object
        """

        self.driver.get(url)

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
                                  for wrapper in self.driver.find_elements_by_css_selector('.cha-paragraph')]

        return chapter

    def is_chapter_locked(self, url=None):
        if url is not None:
            self.driver.get(url)

        return bool(self.driver.find_elements_by_css_selector('.j_locked_chap'))

    def unlock_chapter(self, url=None, coins=False, fastpass=False, unlock_delay=2):
        """
        unlocks the chapter using either coins or fastpass
        if both options are available, coins are given priority

        :required: to be signed in

        :param url: url to chapter
        :param coins: use coins to unlock
        :param fastpass: use fastpass to unlock
        :param unlock_delay: delay between mouse moving to unlock button to clicking.
                             this is introduced as unlock can fail due to some latency issues
        """
        # error testing parameters
        if not coins and not fastpass:
            raise AssertionError('Choose atleast one from "coins" or "fastpass"')

        if url is not None:
            self.driver.get(url)

        # sign in check
        if not self.is_signedin():
            raise NotSignedInError()

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

        WebDriverWait(self.driver, 3)

        button = None
        attempt = True

        if coins and can_coin:
            coin_button = self.driver.find_element_by_css_selector(
                "div[class='lock-group j_lock_btns '] > a[class*='j_unlockChapter']")
            button = coin_button

        elif fastpass and can_fastpass:
            fastpass_button = self.driver.find_element_by_css_selector("div[class^='lock-foot'] > div:nth-child(2) > a")
            button = fastpass_button

        else:
            attempt = False

        if attempt:
            # unlock
            ActionChains(self.driver).move_to_element(button).pause(unlock_delay).click().perform()

    @require_signin
    def batch_unlock(self, coins, fastpass, maximum_cost=5, url=None, execute=True):
        """
        batch unlocks chapters in ascending order

        tries to unlock as efficiently as possible.
        if coins is lower than :param minimum_cost: coins are ignored
        and chapters are unlocked using only fastpass

        :require: to be signed in

        :param coins: amount of coins to use
        :param fastpass: amount of fastpass to use
        :param url: url to novel
        :param maximum_cost: maximum cost of a chapter where coins will be used
        :return: list of unlocked chapters
        """
        if url is not None:
            self.driver.get(url)

        # get all locked chapters
        locked_chapters = []
        toc = self.table_of_contents()
        for chapters in toc.values():
            locked_chapters = locked_chapters + [chapter for chapter in chapters if chapter.locked]

        def explore_forward():

            explored = []

            # skip chapters count of fastpass
            # each fastpass can unlock a chapter
            # so length of fastpass can be unlocked
            # if count is 3, start from index 3, item 4
            i = fastpass

            # iterate through fastpass count
            for c in locked_chapters[:i]:
                chapter = self.chapter(c.url, is_locked=True)

                explored.append(chapter)

            while True:
                # add new chapter
                chapter = self.chapter(locked_chapters[i].url, is_locked=True)
                explored.append(chapter)

                # sort according to cost
                explored.sort(key=lambda c: c.cost)

                # split such that the ones that cost most are assigned to fastpass
                trial_coins, trial_fastpass = explored[:-fastpass], explored[-fastpass:]

                # check if valid solution
                total_trial_coins: int = sum([c.cost for c in trial_coins])
                maximum_allowed_usage = len(trial_coins) * maximum_cost

                # if not valid option
                # previous solution must possible
                # adding the last chapter caused solution to overshoot
                # hence last solution must have maximum unlockable
                if maximum_allowed_usage < total_trial_coins or coins < total_trial_coins:
                    # remove last added to get solution
                    explored.remove(chapter)

                    # sort according to cost
                    explored.sort(key=lambda ch: ch.cost)

                    # split such that the ones that cost most are assigned to fastpass
                    trial_coins, trial_fastpass = explored[:-fastpass], explored[-fastpass:]

                    # return solution
                    return trial_coins, trial_fastpass

                i += 1

        def continuous_bruteforce(modifier=2) -> Tuple[List, List]:
            """
            continues shrinking list until it can be unlocked
            fastpass assigned to highest costing chapters

            :return: list of chapters to be unlocked separated
            """

            # calculate estimate, and limit exploration
            unlockable_estimated_amount = math.floor(coins / maximum_cost) * modifier + fastpass
            unlockable_chapters = [self.chapter(c.url, is_locked=True)
                                   for c in locked_chapters[:unlockable_estimated_amount]]

            # hack: test to confirm all are locked
            assert all([c.locked for c in unlockable_chapters])

            # from all until there is only 1
            for i in range(len(unlockable_chapters), fastpass - 1, -1):

                # sort respect to cost, ascending
                trial_chapters = sorted(unlockable_chapters[:i], key=lambda c: c.cost)

                # split such that the ones that cost most are assigned to fastpass
                trial_coins, trial_fastpass = trial_chapters[:-fastpass], trial_chapters[-fastpass:]

                # check if valid solution
                total_trial_coins = sum([c.cost for c in trial_coins])
                maximum_allowed_usage = len(trial_coins) * maximum_cost
                if maximum_allowed_usage >= total_trial_coins and coins >= total_trial_coins:
                    return trial_coins, trial_fastpass

            return [], []

        # to_coins, to_fastpass = continuous_bruteforce(modifier=2)
        to_coins, to_fastpass = explore_forward()

        if execute:
            # unlock the chapters
            for c in to_coins:
                self.unlock_chapter(c.url, coins=True)
            for c in to_fastpass:
                self.unlock_chapter(c.url, fastpass=True)

        return to_coins, to_fastpass

    def energy_vote(self, indexes: List[int], lead='male', redirect=True):
        """
        votes for the selected indexes of the queue of stories to be released

        :requires: to be signed in

        :param indexes: indexes of stories in queue to energy_vote
        :param lead: either 'male' or 'female' options, to specify which list to select
        :param redirect: whether to load the vote page again
        """

        # to energy_vote screen
        if redirect:
            self.driver.get(f'{BASE_URL}/vote')

        # sign in check
        if not self.is_signedin():
            raise NotSignedInError()

        vote_buttons = [tile.find_element_by_css_selector('._voteBtn')
                        for tile
                        in self.driver.find_elements_by_css_selector(f'#List{lead.capitalize()} > *')]

        for i in indexes:
            vote_buttons[i].click()

    def power_vote(self, url: str = None, repeat: int = 1):
        """
        energy_vote with power stone to :param url:

        :requires: to be signed in

        :param url: url of novel to power up, if this is not specified tries to energy_vote in current page

        :param repeat: number of times to press button.
        :default repeat: 1
        """

        if url is not None:
            self.driver.get(url)

        # sign in check
        if not self.is_signedin():
            raise NotSignedInError()

        # get power stone energy_vote button
        power_button = self.driver.find_element_by_css_selector(".j_power_btn_area > .j_vote_power")

        for _ in range(repeat):
            power_button.click()

    def claim_tasks(self):
        """
        collects all completed task rewards

        :requires: to be signed in
        """

        # sign in check
        if not self.is_signedin():
            raise NotSignedInError()

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
