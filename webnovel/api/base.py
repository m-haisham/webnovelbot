import json
from typing import Dict

import requests

from .cookie import BlockAll
from ..exceptions import ApiError


class BaseApi:
    """
    Creates direct requests to data api rather than to load web page
    """

    def __init__(self):
        # as cookies can lead to a rejected response
        # they are all blocked
        self.session = requests.Session()
        self.session.cookies.set_policy(BlockAll())

    def chapter(self, novel_id, chapter_id) -> Dict:
        response = self.session.get(
            'https://www.webnovel.com/apiajax/chapter/GetContent',
            params={
                '_csrfToken': '',
                'bookId': novel_id,
                'chapterId': chapter_id
            }
        )

        return self.validate(response)

    def toc(self, novel_id) -> Dict:
        response = self.session.get(
            'https://www.webnovel.com/apiajax/chapter/GetChapterList',
            params={
                '_csrfToken': '',
                'bookId': novel_id,
            }
        )

        return self.validate(response)

    def validate(self, response) -> Dict:
        parsed = json.loads(response.text)
        if parsed['code'] != 0:
            raise ApiError(parsed['msg'])

        return parsed
