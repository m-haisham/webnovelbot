from dataclasses import dataclass


@dataclass
class Novel:
    id: str = None
    title: str = None
    synopsis: str = None
    genre: str = None
    url: str = None

    author: str = None
    translator: str = None
    editor: str = None

    views: str = None
    rating: float = None
    review_count: int = None