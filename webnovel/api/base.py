import json
from typing import Dict, List, Union

import requests
from requests.cookies import RequestsCookieJar

from .cookie import BlockAll
from .html import HtmlApi
from ..exceptions import ApiError


class BaseApi:
    """
    Creates direct requests to data api rather than to load web page
    """

    def __init__(self, cookies: Union[RequestsCookieJar, List[dict], None] = None):
        # as cookies can lead to a rejected response
        # they are all blocked
        self.session = requests.Session()
        self.has_cookies = bool(cookies)

        # set cookies
        if type(cookies) == RequestsCookieJar:
            self.session.cookies = cookies
        elif type(cookies) == list:
            for cookie in cookies:
                cookie = {key: value for key, value in cookie.items() if key not in ['httpOnly', 'expiry', 'sameSite']}
                m_cookie = requests.cookies.create_cookie(**cookie)
                self.session.cookies.set_cookie(m_cookie)
        elif cookies is None:
            self.session.cookies.set_policy(BlockAll())
            pass
        else:
            raise TypeError("'cookies' was of unrecognized type; must be (RequestsCookieJar, List[dict cookie], None)")

        # html api
        self.html = HtmlApi(self.session)

    def chapter(self, novel_id: int, chapter_id: int) -> Dict:
        response = self.session.get(
            'https://www.webnovel.com/go/pcm/chapter/getContent',
            params={
                # '_csrfToken': self.session.cookies.get('_csrfToken') if self.has_cookies else '',
                'bookId': novel_id,
                'chapterId': chapter_id
            }
        )

        return self.validate(response)

    def toc(self, novel_id: int) -> Dict:
        response = self.session.get(
            'https://www.webnovel.com/apiajax/chapter/GetChapterList',
            params={
                '_csrfToken': self.session.cookies.get('_csrfToken') if self.has_cookies else '',
                'bookId': novel_id,
            }
        )

        return self.validate(response)

    def unlock(self, novel_id: int, chapters: List[Dict], unlock_type: int):
        """
        Unlocks chapters provided with method specified

        Requires cookies

        :param novel_id: id of novel
        :param chapters: list of dict objects containing the following keys,
         [chapterPrice: int],
         [chapterId: str],
         [chapterType: int]

        :param unlock_type: 3 to unlock with coins | 5 to unlock with fastpass
        :return:
        """

        response = self.session.post(
            'https://www.webnovel.com/apiajax/SpiritStone/useSSAjax',
            data={
                '_csrfToken': self.session.cookies.get('_csrfToken') if self.has_cookies else '',
                'bookId': novel_id,
                'chapters': json.dumps(chapters),
                'unlockType': unlock_type
            }
        )

        return self.validate(response)

    def power_vote(self, novel_id):
        """
        Applies single power stone vote to novel

        Requires cookies

        :param novel_id: novel to vote
        :return: Response
        """
        response = self.session.post(
            'https://www.webnovel.com/apiajax/powerStone/vote',
            data={
                '_csrfToken': self.session.cookies.get('_csrfToken') if self.has_cookies else '',
                'bookId': novel_id,
                'novelType': 0
            }
        )

        return self.validate(response)

    def energy_vote(self, novel_id):
        """
        Applies single energy stone vote to translation novel release queue

        Requires cookies

        :param novel_id: novel to vote
        :return: Response
        """
        response = self.session.post(
            'https://www.webnovel.com/apiajax/translationVote/vote',
            data={
                '_csrfToken': self.session.cookies.get('_csrfToken') if self.has_cookies else '',
                'bookId': novel_id
            }
        )

        return self.validate(response)

    def validate(self, response) -> Dict:
        parsed = json.loads(response.content)
        if parsed['code'] != 0:
            raise ApiError(parsed['msg'])

        return parsed
