from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Novel:
    id: str = None
    title: str = None
    synopsis: str = None
    genre: str = None
    url: str = None
    cover_url: str = None

    author: str = None
    translator: str = None
    editor: str = None

    views: str = None
    rating: float = None
    review_count: int = None

    @staticmethod
    def from_url(url):
        """
        scrape novel information from webnovel

        :param url: url to novel
        :return: Novel object
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        info_elems = soup.select('._mn > *')
        subinfo_elems = info_elems[1].select(':scope > *')
        writerinfo_elems = info_elems[2].select('p > *')

        novel = Novel()
        novel.id = int(url.split('/')[4])
        novel.title = info_elems[0].text[:-len(info_elems[0].find('small').text) - 1],
        novel.title = novel.title[0]

        novel.synopsis = soup.select_one("div[class*='j_synopsis'] > p").text
        novel.genre = subinfo_elems[0].text.strip(),
        novel.views = subinfo_elems[-1].text[:-6].strip(),
        novel.url = url[:]
        novel.cover_url = f'https://img.webnovel.com/bookcover/{novel.id}'

        try:
            # ratings are posted up to 5, they are converted to float and normalized to 1
            novel.rating = float(info_elems[3].find('strong').text) / 5.0,
            novel.rating = novel.rating[0]
        except ValueError:
            # no ratings
            novel.rating = None

        try:
            # stripped of all non numerals and converted to int
            novel.review_count = int(
                info_elems[3].find('small').text.strip('()')[:-8].replace(',', ''))
        except ValueError:
            # not enough reviews
            novel.review_count = None

        # writer info
        for i in range(round(len(writerinfo_elems) / 2)):
            label = writerinfo_elems[i * 2].text.strip(': ').lower()
            value = writerinfo_elems[i * 2 + 1].text

            setattr(novel, label, value)

        return novel
