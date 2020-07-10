from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class Profile:
    id: int = None
    coins: int = None
    fastpass: int = None
    power_stone: int = None
    energy_stone: int = None

    fields = ['coins', 'fastpass', 'power_stone', 'energy_stone']

    @staticmethod
    def from_html(html: str, user_id=None):
        """
        get profile info using user id

        [html] can be obtained through, BaseApi.html.profile with cookies.
        [user_id] can be obtained through WebnovelBot.user_id.

        :param html: profile page
        :param user_id: id of user profile
        :return: profile of user
        """
        soup = BeautifulSoup(html, 'lxml')

        profile = Profile(id=user_id)

        group = soup.select("div[class='fl'] > a.dib.mr32, div[class='fl'] > a.dib.mr16")

        profile.coins = int(group[0].text)
        profile.fastpass = int(group[1].text)
        profile.power_stone = int(group[2].text)
        profile.energy_stone = int(group[3].text)

        return profile
