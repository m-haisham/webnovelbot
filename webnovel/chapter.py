from dataclasses import dataclass
from typing import List


@dataclass
class Chapter:
    no: int = None
    url: str = None
    title: str = None
    paragraphs: List[str] = None
    locked: bool = None
    cost: int = None
