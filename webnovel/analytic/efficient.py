from typing import List, Callable

from . import Analysis
from .interface import IAnalyser
from ..api import ParsedApi
from ..models import Chapter, Novel, Profile


class Efficient(IAnalyser):
    """
    Calculate while abiding by the rules:
     - cheaper chapters with coins
     - expensive chapters with fastpass
     - chapters unlocked using coins must not exceed [maximum_cost] individually

    if [maximum_cost] is less than 0 it is considered as being infinite
    """

    def __init__(self, novel: Novel, profile: Profile, maximum_cost=-1, on_load: Callable[[Chapter], None] = None):
        """
        :param novel: attribute id must not be null
        :param profile: webnovel profile, require [coins] and [fastpass]
        :param maximum_cost: maximum coins to spend a single chapter, maximum
        :param on_load: call when chapter is loaded
        """
        self.novel = novel
        self.profile = profile
        self.maximum_cost = maximum_cost

        if on_load is None:
            self.on_load = lambda c: None
        else:
            self.on_load = on_load

        self._api = ParsedApi()

    def analyse(self, chapters: List[Chapter]) -> Analysis:

        coins = self.profile.coins
        fastpass = self.profile.fastpass

        if coins <= 0 and fastpass <= 0:
            return Analysis.empty()

        # get cost
        for i in range(len(chapters)):
            if chapters[i].cost is None:
                chapters[i] = self._api.chapter(self.novel.id, chapters[i].id)
            self.on_load(chapters[i])

        # sort according to cost
        chapters.sort(key=lambda c: c.cost)

        if fastpass == 0:
            not_chosen = chapters
            via_fastpass = []
        else:
            not_chosen, via_fastpass = chapters[:-fastpass], chapters[-fastpass:]

        # get smallest possible coins cost to fit profile
        via_coins: List[Chapter] = []
        for chapter in not_chosen:
            total_cost = sum([c.cost for c in via_coins])

            if total_cost + chapter.cost > coins:
                break

            # maximum cost less than 0, means maximum cost is ignored
            # ending search as subsequent chapters would have higher or equal cost as list is sorted
            if 0 <= self.maximum_cost < chapter.cost:
                break

            via_coins.append(chapter)

        return Analysis(via_coins=via_coins, via_fastpass=via_fastpass)
