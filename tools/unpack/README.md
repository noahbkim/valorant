# Unpack

A short, brittle utility for unpacking assets from Riot's Valorant asset dump.
Also comes with an organizer for personal use; feel free to copy and hack.
Currently, the unpacker automatically converts images from TGA to PNG via PIL.

Requires `requests` and `Pillow`.

## Usage

To use the unpacker:

```commandline
# Download the most recent asset archive and unpack every file (URL is hardcoded) 
$ python3.9 unpack.py -d

# Download a specific URL and unpack every file
$ python3.9 unpack.py -d https://valorant.dyn.riotcdn.net/x/content-catalog/PublicContentCatalog-release-03.00.zip

# Unpack a local archive, e.g. PublicContentCatalog-release-03.00.zip
$ python3.9 unpack.py -f ./PublicContentCatalog-release-03.00.zip

# Unpack with a certain prefix (works for both -d and -f)
$ python3.9 unpack.py -f ./PublicContentCatalog-release-03.00.zip -p Maps

# Unpack with multiple prefixes
$ python3.9 unpack.py -f ./PublicContentCatalog-release-03.00.zip -p Maps Weapons
```

Currently, organize shuffles the map files into organized folders with each image as `map.png`, `splash.png`, and `thumbnail.png`.
To use it, run the following:

```commandline
$ python3.9 organize.py ./unpacked/ --maps 
```

## Setup

If you prefer, you can use the included `Pipfile` to create a virtual environment for this project.
