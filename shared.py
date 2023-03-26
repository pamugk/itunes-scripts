from enum import Enum
import re

tags = [
    ("soal", "\xa9alb"),
    ("soaa", "aART"),
    ("soar", "\xa9ART"),
    ("sonm", "\xa9nam"),
    ("soco", "\xa9wrt"),
]
track_number_regex = re.compile(r"^(\d+)-(\d+)|^(\d+)")


class Scope(str, Enum):
    LIBRARY = "library",
    ARTIST = "artist",
    ALBUM = "album"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
