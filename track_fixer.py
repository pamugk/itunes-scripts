import argparse
import csv
from mutagen.mp4 import MP4
import os
from shared import Scope, tags, track_number_regex

genres = dict()


def fix_track(track_path, track_number, disk_number, is_compilation):
    track = MP4(track_path)
    for tag in tags:
        if tag[0] in track:
            track[tag[1]] = track[tag[0]]
    track["trkn"] = [track_number]
    track["disk"] = [disk_number]
    track["cpil"] = is_compilation
    if "geID" in track:
        genre_id = track["geID"][0]
        if genre_id in genres:
            track["\xa9gen"] = [genres[genre_id]]
    track.save()


def scan_album(album_path, is_compilation):
    if os.path.isfile(album_path):
        return

    disk_sizes = dict()
    tracks_disks = dict()
    tracks_positions = dict()
    tracks = list()

    for filename in os.scandir(album_path):
        if filename.is_file() and filename.name.endswith(".m4a"):
            track_positions = track_number_regex.search(filename.name)
            if track_positions[1] is None:
                disk = 1
                position = int(track_positions[3])
            else:
                disk = int(track_positions[1])
                position = int(track_positions[2])
            disk_sizes[disk] = disk_sizes.setdefault(disk, 0) + 1
            tracks_disks[filename.name] = disk
            tracks_positions[filename.name] = position
            tracks.append((filename.name, filename.path))

    disk_count = len(disk_sizes)
    for track in tracks:
        track_name = track[0]
        track_path = track[1]
        disk = tracks_disks[track_name]
        track_number = (tracks_positions[track_name], disk_sizes[disk])
        disk_number = (disk, disk_count)
        fix_track(track_path, track_number, disk_number, is_compilation)


def scan_artist(artist_path):
    if os.path.isfile(artist_path):
        return
    is_compilation = os.path.basename(artist_path) == "Compilations"
    for album_dir_name in os.scandir(artist_path):
        if album_dir_name.is_dir():
            scan_album(album_dir_name.path, is_compilation)


def scan_library(library_path):
    if os.path.isfile(library_path):
        return
    for artist_dir_name in os.scandir(library_path):
        if artist_dir_name.is_dir():
            scan_artist(artist_dir_name.path)


parser = argparse.ArgumentParser(description="Fix iTunes files metadata. ")
parser.add_argument("path")
parser.add_argument("-c", "--compilation", action="store_true")
parser.add_argument("-g", "--genres")
parser.add_argument("-s", "--scope", choices=Scope.list(), required=True)
args = parser.parse_args()

if not os.path.exists(args.path):
    raise FileNotFoundError("Analyzed directory not found")

if args.genres is not None and os.path.exists(args.genres):
    with open(genres, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            genres[int(row["id"])] = row["name"]

match args.scope:
    case Scope.LIBRARY:
        scan_library(args.path)
    case Scope.ARTIST:
        scan_artist(args.path)
    case Scope.ALBUM:
        scan_album(args.path, args.compilation)
