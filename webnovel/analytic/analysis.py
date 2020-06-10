from dataclasses import dataclass
from typing import List

from ..models import Chapter


@dataclass
class Analysis:
    via_coins: List[Chapter]
    via_fastpass: List[Chapter]

    @staticmethod
    def empty():
        return Analysis(via_coins=[], via_fastpass=[])

    @property
    def coins_cost(self):
        return sum([c.cost for c in self.via_coins])

    @property
    def fastpass_cost(self):
        return len(self.via_fastpass)
