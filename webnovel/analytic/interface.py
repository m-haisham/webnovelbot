from typing import List

from .analysis import Analysis
from ..models import Chapter


class IAnalyser:
    def analyse(self, chapters: List[Chapter]) -> Analysis:
        """
        :param chapters: chapters to be analysed. they must be locked
        :return: analysis object
        """
        raise NotImplementedError('method not overridden')
