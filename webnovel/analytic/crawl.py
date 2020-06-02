from typing import List, Callable

from .analysis import Analysis
from .interface import IAnalyser
from ..models import Profile, Chapter


class ForwardCrawl(IAnalyser):
    def __init__(self, profile: Profile, maximum_cost, on_load: Callable[[Chapter], None] = None):
        """
        :param profile: webnovel profile for coins and fastpass
        :param maximum_cost: maximum coins to spend a single chapter
        :param on_load: call when chapter is loaded
        """
        self.profile = profile
        self.maximum_cost = maximum_cost

        if on_load is None:
            self.on_load = lambda c: None
        else:
            self.on_load = on_load

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
            chapter = Chapter(url=c.url).load()
            self.on_load(chapter)

            explored.append(chapter)

        while True:
            # add new chapter
            chapter = Chapter(url=chapters[i].url).load()
            self.on_load(chapter)

            explored.append(chapter)

            # sort according to cost
            explored.sort(key=lambda ch: ch.cost)

            # split such that the ones that cost most are assigned to fastpass
            trial_coins, trial_fastpass = explored[:-fastpass], explored[-fastpass:]

            # check if valid solution
            total_trial_coins: int = sum([c.cost for c in trial_coins])
            maximum_allowed_usage = len(trial_coins) * self.maximum_cost

            # if not valid option
            # previous solution must possible
            # adding the last chapter caused solution to overshoot
            # hence last solution must have maximum unlockable
            if maximum_allowed_usage < total_trial_coins or coins < total_trial_coins:
                # remove last added to get solution
                explored.remove(chapter)

                # sort according to cost
                explored.sort(key=lambda ch: ch.cost)

                # split such that the ones that cost most are assigned to fastpass
                trial_coins, trial_fastpass = explored[:-fastpass], explored[-fastpass:]

                # return solution
                return Analysis(via_coins=trial_coins, via_fastpass=trial_fastpass)

            i += 1
