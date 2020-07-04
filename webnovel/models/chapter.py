import json
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

from ..decorators import deprecated


@dataclass
class Chapter:
    no: int = None
    id: int = None
    url: str = None
    title: str = None
    paragraphs: List[str] = None
    locked: bool = None
    cost: int = None
    type: int = None

    @deprecated('use Webnovel.api.ParsedApi.chapter instead')
    def load(self):
        data = requests.get(self.url)

        soup = BeautifulSoup(data.content, 'html.parser')
        locked_content = soup.find('div', {'class': 'j_locked_chap'})

        self.id = self.chapter_id_from_url()

        self.no = int(soup.find('span', {'class': 'j_chapIdx'}).text.strip('Chapter ')[:-1])
        self.title = soup.find('div', {'class': 'cha-tit'}).find('h3').text
        self.locked = locked_content is not None

        if self.locked:
            params = json.loads(locked_content.find('a', {'class': '_bt_unlock'})['data-unlock-params'])
            self.cost = params['chapterPrice']

        return self

    def chapter_id_from_url(self) -> int:
        return int(self.url.split('/')[5])

    def novel_id_from_url(self) -> int:
        return int(self.url.split('/')[4])
