from typing import List, Callable

from . import Analysis
from .interface import IAnalyser
from ..api import ParsedApi
from ..models import Chapter, Profile, Novel


class HardLine(IAnalyser):
    """
    Calculate while abiding by the rules:
    - chapter cost less than or equal to [coins_line] would be selected as coins
    - chapter cost higher than or equal to [fastpass_line] would be select as fastpass
    """

    def __init__(self, novel: Novel, profile: Profile, coins_line: int = None, fastpass_line: int = None,
                 on_load: Callable[[Chapter], None] = None):
        """
        [fastpass_line] and [coins_line] are used to determine which is selected for which

        :param novel: attribute id must not be null
        :param profile: webnovel profile, require [coins] and [fastpass]
        :param coins_line: chapters with cost less that or equal are selected for coins
        :param fastpass_line: chapters with cost greater than or equal are selected for fastpass
        :raises ValueError: if [fastpass_line] is less than [coins_line] or if both lines are None
        """
        self.novel = novel
        self.profile = profile

        if coins_line is not None and fastpass_line is not None:
            if coins_line >= fastpass_line:
                raise ValueError('[coins_line] must be less than [fastpass_line]')
        elif coins_line is None and fastpass_line is None:
            raise ValueError('either [coins_line] or [fastpass_line] must not be "None"')

        self.fastpass_line = fastpass_line
        self.coins_line = coins_line

        if on_load is None:
            self.on_load = lambda c: None
        else:
            self.on_load = on_load

        self._api = ParsedApi()

    def analyse(self, chapters: List[Chapter]) -> Analysis:

        coins = self.profile.coins
        fastpass = self.profile.fastpass

        # flags
        coins_maxed = self.coins_line is None or coins == 0
        fastpass_maxed = self.fastpass_line is None or fastpass == 0

        analysis = Analysis.empty()
        for chapter in chapters:

            # making sure chapter has cost attribute populated
            # if not requesting for chapter cost
            if chapter.cost is None:
                chapter = self._api.chapter(self.novel.id, chapter.id)

            self.on_load(chapter)

            coins_cost = analysis.coins_cost
            fastpass_cost = analysis.fastpass_cost

            # distribute
            if not coins_maxed:
                # check whether adding the chapter will exceed coins balance
                if coins_cost + chapter.cost <= coins and chapter.cost <= self.coins_line:
                    analysis.via_coins.append(chapter)
                    coins_cost += chapter.cost

            elif not fastpass_maxed and chapter.cost >= self.fastpass_line:
                analysis.via_fastpass.append(chapter)

                fastpass_cost += 1
                fastpass_maxed = fastpass == fastpass_cost

            if coins_maxed and fastpass_maxed:
                break

        return analysis
