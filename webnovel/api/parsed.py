from typing import List, Dict

from bs4 import BeautifulSoup

from .base import BaseApi
from ..models import Chapter


class UnlockType:
    coins = 3
    fastpass = 5


class ParsedApi(BaseApi):
    def toc(self, novel_id) -> Dict[str, List[Chapter]]:
        response = super().toc(novel_id)

        volume_items = response['data']['volumeItems']

        volumes = {}
        for volume_item in volume_items:
            chapters = [
                Chapter(
                    no=item['index'],
                    id=item['id'],
                    url=f'https://www.webnovel.com/book/{novel_id}/{item["id"]}',
                    title=item['name'],
                    locked=not int(item['isAuth']),
                ) for item in volume_item['chapterItems']
            ]

            _name = volume_item['name']
            volume_name = f'Volume {volume_item["index"]}' + (f': {_name}' if _name else '')
            volumes[volume_name] = chapters

        return volumes

    def chapter(self, novel_id, chapter_id) -> Chapter:
        response = super().chapter(novel_id, chapter_id)

        data = response['data']['chapterInfo']

        return Chapter(
            no=data['chapterIndex'],
            id=data['chapterId'],
            title=data['chapterName'],
            url=f'https://www.webnovel.com/book/{novel_id}/{chapter_id}',
            paragraphs=[para['content'] for para in data['contents']],
            cost=data['price'],
            locked=not int(data['isAuth']),
            type=int(data['chapterLevel']),
        )

    def unlock(self, novel_id: int, chapter: Chapter, unlock_type: int) -> Chapter:
        """
        Unlocks chapters provided with options specified

        :param novel_id: corresponding novel
        :param chapter: chapter to unlock
        :param unlock_type: use UnlockType attributes to get correct ints
        :return: unlocked chapters
        """

        # check and convert to viable form data
        form_data = [{
            'chapterPrice': chapter.cost if unlock_type == UnlockType.coins else 1,
            'chapterId': str(chapter.id),
            'chapterType': 2  # no idea why its 2, but it seems to work
        }]

        response = super().unlock(novel_id, form_data, unlock_type)

        data = response['data']

        # update paragraph data
        chapter.paragraphs = [BeautifulSoup(para['content'], 'lxml').text for para in data['contents']]

        return chapter
