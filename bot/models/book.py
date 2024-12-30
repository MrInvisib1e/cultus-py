from enum import Enum
from typing import List, Optional


class BookRating(Enum):
    G = 0
    M = 10
    R = 20
    RE = 30

    @property
    def rating_text(self):
        return {
            BookRating.G: "Загальний (G) | 0+",
            BookRating.M: "Дорослий (M) | 15+",
            BookRating.R: "Обмежений (R) | 18+",
            BookRating.RE: "Екстремальний (RE) | 21+"
        }.get(self, "")


class BookSize(Enum):
    MICRO = 0
    MINI = 10
    MIDI = 20
    MAXI = 30
    EPIC = 40
    LEGEND = 50

    @property
    def size_text(self):
        return {
            BookSize.MICRO: "Мікро",
            BookSize.MINI: "Міні",
            BookSize.MIDI: "Міді",
            BookSize.MAXI: "Максі",
            BookSize.EPIC: "Епічний",
            BookSize.LEGEND: "Легендарний"
        }.get(self, "")


class BookStatus(Enum):
    IN_PROGRESS = 0
    COMPLETED = 10
    ON_HOLD = 20
    DROPPED = 30

    @property
    def status_text(self):
        return {
            BookStatus.IN_PROGRESS: "В процесі",
            BookStatus.COMPLETED: "Завершений",
            BookStatus.ON_HOLD: "Заморожений",
            BookStatus.DROPPED: "Закинутий"
        }.get(self, "")


class BookUser:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class BookPair:
    def __init__(self, first_character: dict, second_character: dict):
        self.first_character = first_character
        self.second_character = second_character


class BookTag:
    def __init__(self, title: str):
        self.title = title


class Book:
    def __init__(self, id: int, title: str, likes_count: int, description: str, author: BookUser,
                 is_translation: bool, original_link: str, rating: BookRating, book_size: Optional[BookSize],
                 expected_book_size: Optional[BookSize], pages_count: int, book_status: BookStatus,
                 pairings: List[BookPair], tags: List[BookTag]):
        self.id = id
        self.title = title
        self.likes_count = likes_count
        self.description = description
        self.author = author
        self.is_translation = is_translation
        self.original_link = original_link
        self.rating = rating
        self.book_size = book_size
        self.expected_book_size = expected_book_size
        self.pages_count = pages_count
        self.book_status = book_status
        self.pairings = pairings
        self.tags = tags

    @property
    def rating_text(self):
        return self.rating.rating_text

    @property
    def book_size_text(self):
        return self.book_size.size_text if self.book_size else ""

    @property
    def expected_book_size_text(self):
        return self.expected_book_size.size_text if self.expected_book_size else ""

    @property
    def book_status_text(self):
        return self.book_status.status_text