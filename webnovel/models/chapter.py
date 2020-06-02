import json
from typing import List

import requests
from bs4 import BeautifulSoup


class Chapter:
    no: int = None
    id: int = None
    url: str = None
    title: str = None
    paragraphs: List[str] = None
    locked: bool = None
    cost: int = None

    def __init__(self, no=None, _id=None, url=None, title=None, paragraphs=None, locked=None, cost=None):
        self.no = no
        self.id = _id
        self.url = url
        self.title = title
        self.paragraphs = paragraphs
        self.locked = locked
        self.cost = cost

    def load(self):
        data = requests.get(self.url)

        soup = BeautifulSoup(data.content, 'html.parser')
        locked_content = soup.find('div', {'class': 'j_locked_chap'})

        self.id = self.id_from_url()

        self.no = int(soup.find('span', {'class': 'j_chapIdx'}).text.strip('Chapter ')[:-1])
        self.title = soup.find('div', {'class': 'cha-tit'}).find('h3').text
        self.locked = locked_content is not None

        if self.locked:
            params = json.loads(locked_content.find('a', {'class': '_bt_unlock'})['data-unlock-params'])
            self.cost = params['chapterPrice']

        return self

    def id_from_url(self) -> int:
        return int(self.url.split('/')[5])
