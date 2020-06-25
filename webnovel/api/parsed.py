from typing import List

from .base import BaseApi
from ..models import Chapter


class ParsedApi(BaseApi):
    def toc(self, novel_id) -> List[List[Chapter]]:
        response = super().toc(novel_id)

        volume_items = response['data']['volumeItems']

        volumes = []
        for volume_item in volume_items:
            chapters = [
                Chapter(
                    no=item['index'],
                    id=item['id'],
                    url=f'https://www.webnovel.com/book/{novel_id}/{item["id"]}',
                    title=item['name'],
                ) for item in volume_item['chapterItems']
            ]

            volumes.append(chapters)

        return volumes

    def chapter(self, novel_id, chapter_id) -> Chapter:
        response = super().chapter(novel_id, chapter_id)

        info = response['data']['chapterInfo']

        return Chapter(
            no=info['chapterIndex'],
            id=info['chapterId'],
            title=info['chapterName'],
            url=f'https://www.webnovel.com/book/{novel_id}/{chapter_id}',
            paragraphs=[para['content'][3:-4] for para in info['contents']],
            cost=info['SSPrice'],
        )
