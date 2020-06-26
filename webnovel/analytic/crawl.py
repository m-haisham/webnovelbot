from typing import List, Callable

from .analysis import Analysis
from .interface import IAnalyser
from ..api import ParsedApi
from ..models import Profile, Chapter, Novel


class ForwardCrawl(IAnalyser):
    """
    Calculate while abiding by the rules:
     - all chapters must be unlocked continuously
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

        explored = []

        # skip chapters count of fastpass
        # each fastpass can unlock a chapter
        # so length of fastpass can be unlocked
        # if count is 3, start from index 3, item 4
        i = fastpass

        # iterate through fastpass count
        for c in chapters[:i]:
            chapter = self._api.chapter(self.novel.id, c.id)
            self.on_load(chapter)

            explored.append(chapter)

        while True:
            # add new chapter
            chapter = self._api.chapter(self.novel.id, chapters[i].id)
            self.on_load(chapter)

            explored.append(chapter)

            # sort according to cost
            explored.sort(key=lambda ch: ch.cost)

            # split such that the ones that cost most are assigned to fastpass
            trial_coins, trial_fastpass = self._split(explored, fastpass)

            # check if valid solution
            total_trial_coins: int = sum([c.cost for c in trial_coins])

            # if maximum cost is positive check chapters
            # else maximum cost is regarded as being infinite.
            overshooted = any([c.cost > self.maximum_cost for c in trial_coins]) if self.maximum_cost >= 0 else False

            # if not valid option
            # previous solution must possible
            # adding the last chapter caused solution to overshoot
            # hence last solution must have maximum unlockable
            if overshooted or coins < total_trial_coins:
                # remove last added to get solution
                explored.remove(chapter)

                # sort according to cost
                explored.sort(key=lambda ch: ch.cost)

                # split such that the ones that cost most are assigned to fastpass
                trial_coins, trial_fastpass = self._split(explored, fastpass)

                # return solution
                return Analysis(via_coins=trial_coins, via_fastpass=trial_fastpass)

            i += 1

    def _split(self, chapters: List, fastpass: int):
        """
        split chapters so that most expensive will be to fastpass

        :param chapters: sorted chapters to split
        :param fastpass: amount of fastpass
        :return: coins, fastpass
        """
        if fastpass == 0:
            return chapters, []
        else:
            return chapters[:-fastpass], chapters[-fastpass:]
