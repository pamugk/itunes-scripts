import argparse
import os
from shared import Scope, track_number_regex


def analyze_album(album_path):
    if os.path.isfile(album_path):
        return

    tracks_positions = dict()
    for filename in os.scandir(album_path):
        if filename.is_file() and filename.name.endswith(".m4a"):
            track_positions = track_number_regex.search(filename.name)
            if track_positions[1] is None:
                position = (1, int(track_positions[3]))
            else:
                position = (int(track_positions[1]), int(track_positions[2]))
            tracks_positions.setdefault(position, []).append(filename.path)

    for position in tracks_positions:
        if len(tracks_positions[position]) > 1:
            print(tracks_positions[position])


def analyze_artist(artist_path):
    if os.path.isfile(artist_path):
        return

    for album_dir_name in os.scandir(artist_path):
        if album_dir_name.is_dir():
            analyze_album(album_dir_name.path)


def analyze_library(library_path):
    if os.path.isfile(library_path):
        return

    for artist_dir_name in os.scandir(library_path):
        if artist_dir_name.is_dir():
            analyze_artist(artist_dir_name.path)


parser = argparse.ArgumentParser(description="Scan iTunes library for duplicates. ")
parser.add_argument("path")
parser.add_argument("-s", "--scope", choices=Scope.list(), required=True)
args = parser.parse_args()
if not os.path.exists(args.path):
    raise FileNotFoundError("Analyzed directory not found")
match args.scope:
    case Scope.LIBRARY:
        analyze_library(args.path)
    case Scope.ARTIST:
        analyze_artist(args.path)
    case Scope.ALBUM:
        analyze_album(args.path)
