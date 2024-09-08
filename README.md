# TMDB Bulk Posters Downloader

Basic CLI to download posters from The Movie Database (TMDB) in bulk.

## Prerequisites

Python 3.10 or later. No additional dependencies! 

A [TMDB API key](https://www.themoviedb.org/documentation/api) exported as `TMDB_KEY` in your
environment or saved in a `.TMDB_KEY` file.

## Usage

```
usage: python download.py [-h] [--file [FILE]] [--width WIDTH] [--source SOURCE] [--out OUT]

options:
  -h, --help            show this help message and exit
  --file [FILE], -f [FILE]
                        Input file with movie ids. Defaults to stdin.
  --width WIDTH, -w WIDTH
                        Desired poster width: 92, 154, 185, 342, 500, 780, original (default: original)
  --source SOURCE, -s SOURCE
                        Source platform of the movie ids: tmdb, imdb, youtube, ... (default: imdb)
  --out OUT, -o OUT     Output directory. (default: ./posters)
```

### Examples:

```bash
python download.py -f imdb_ids.txt -w 500 -o ./posters
```

```bash
echo "tt0101258 tt0118694 tt0212712" | python download.py -w 154 -o ./wkw_thumbnails
```

```bash
echo "PixarWallE" | python download.py -s facebook -o .
```
