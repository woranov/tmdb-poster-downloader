import argparse
import functools
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Iterator, Literal

VERSION = "0.1.0"

# as per https://api.themoviedb.org/3/configuration
WIDTHS = (92, 154, 185, 342, 500, 780, "original")
Width = int | Literal["original"]

POSTER_PATH_TMPL = "https://image.tmdb.org/t/p/{width}/{path}"

USER_AGENT = f"https://github.com/woranov/tmdb-poster-downloader ({VERSION})"


@functools.cache
def get_headers():
    key = os.getenv("TMDB_KEY")
    if key is None:
        if (key_file_path := Path(".TMDB_KEY")).exists():
            key = key_file_path.read_text().strip()

    if key is None:
        print(
            "ERROR: TMDB_KEY not provided. Set TMDB_KEY or create a .TMDB_KEY file in current working directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {key}",
        "User-Agent": USER_AGENT,
    }


def make_api_request(url):
    req = urllib.request.Request(url, headers=get_headers())
    with urllib.request.urlopen(req) as f:
        return json.load(f)


def get_poster_url(movie_id: str, width: Width = "original", source="imdb"):
    if source == "tmdb":
        movie = make_api_request(f"https://api.themoviedb.org/3/movie/{movie_id}")
    else:
        data = make_api_request(
            f"https://api.themoviedb.org/3/find/{movie_id}?external_source={source}_id"
        )
        if data.get("movie_results"):
            movie = data["movie_results"][0]
        else:
            print(f"Movie not found for {source} id: {movie_id}", file=sys.stderr)
            sys.exit(1)

    width_s = f"w{width}" if isinstance(width, int) else width
    poster_path = movie["poster_path"].lstrip("/")
    return POSTER_PATH_TMPL.format(width=width_s, path=poster_path)


def download_poster(poster_url: str, path: Path):
    if path.exists():
        return False

    with urllib.request.urlopen(poster_url) as resp, path.open("wb") as f:
        if resp.status != 200:
            print(f"failed with status {resp.status}")
            return False

        f.write(resp.read())

    return True


def download_posters(
    ids: Iterator[str], out_dir: Path, width: Width = "original", source="imdb"
):
    out_dir.mkdir(exist_ok=True)

    for id in ids:
        # TODO: in case tmdb starts using other image formats we should future-proof this using the
        #   actual poster data from the API
        file_name = f"{id}.jpg"
        path = out_dir / file_name

        if path.exists():
            print(path, "already downloaded")
            continue

        poster_url = get_poster_url(id, width=width, source=source)
        if download_poster(poster_url, path):
            print(path)


def convert_width(width: str) -> Width:
    if width == "original":
        return width
    if width.isnumeric():
        return int(width)

    raise ValueError(f"Invalid width: {width}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file with movie ids. Defaults to stdin.",
    )
    parser.add_argument(
        "--width",
        "-w",
        type=convert_width,
        default="original",
        help=f"Desired poster width: {', '.join(map(str, WIDTHS))} (default: original)",
    )
    parser.add_argument(
        "--source",
        "-s",
        default="imdb",
        help="Source platform of the movie ids: tmdb, imdb, youtube, ... (default: imdb)",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=Path,
        default=Path("posters"),
        help="Output directory. (default: ./posters)",
    )

    args = parser.parse_args()

    if args.file.isatty():
        parser.print_help()
        return 1

    ids = args.file.read().strip().split()

    download_posters(ids, out_dir=args.out, width=args.width, source=args.source)


if __name__ == "__main__":
    sys.exit(main())
