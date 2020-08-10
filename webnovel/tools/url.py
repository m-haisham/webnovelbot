from typing import Tuple


class UrlTools:
    """
    url conversion tool to and from [novel_id], [chapter_id], and [profile_id]
    """
    base_url = 'https://www.webnovel.com/book'

    @staticmethod
    def to_novel_url(novel_id):
        """
        :return: novel url
        """
        return f'{UrlTools.base_url}/{novel_id}'

    @staticmethod
    def from_novel_url(novel_url):
        """
        :return: url of novel
        """
        try:
            return int(novel_url.split('/')[4])
        except ValueError:
            return int(novel_url.split('_')[-1])

    @staticmethod
    def to_chapter_url(novel_id, chapter_id):
        """
        :return: chapter url
        """
        return f'{UrlTools.base_url}/{novel_id}/{chapter_id}'

    @staticmethod
    def from_chapter_url(chapter_url) -> Tuple[int, int]:
        """
        :return: novel_id, chapter_id
        """
        pieces = chapter_url.split('/')
        try:
            return int(pieces[4]), int(pieces[5])
        except ValueError:
            return int(pieces[4].split('_')[-1]), int(pieces[5].split('_')[-1])

    @staticmethod
    def to_profile_url(profile_id):
        """
        :return: profile url
        """
        return f'https://www.webnovel.com/profile/{profile_id}?appId=10'

    @staticmethod
    def from_profile_url(profile_url):
        """
        :return: profile id
        """
        return int(profile_url.split('/')[4].split('?')[0])
