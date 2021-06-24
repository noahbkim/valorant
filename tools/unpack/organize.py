import shutil
from pathlib import Path


MAPS = {
    "2bee0dc9-4ffe-519b-1cbd-7fbe763a6047": "haven",
    "2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba": "bind",
    "d960549e-485c-e861-8d71-aa9d1aed12a2": "split",
    "e2ad5c54-4114-a870-9641-8ea21279579a": "icebox",
    "7eaecc1b-4337-bbf6-6ab9-04b8f06b3319": "ascent",
    "2fb9a4fd-47b8-4e7d-a969-74b4046ebd53": "breeze",
    "ee613ee9-28b7-4beb-9666-08db13bb2244": "training",}

MAP_SPECIFIERS = {
    None: "map",
    "splash": "splash",
    "listview": "thumbnail",
}


def main():
    """Do some custom file organization."""

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("unpacked")
    parser.add_argument("-m", "--maps", action="store_true", required=True)

    args = parser.parse_args()

    unpacked_path = Path(args.unpacked)

    if args.maps:
        maps_path = unpacked_path.joinpath("Maps")
        for path in maps_path.glob("*"):
            if not path.is_file() or "." not in path.parts[-1]:
                continue

            name, extension = path.parts[-1].rsplit(".", maxsplit=1)
            uid, specifier = (name.lower().split("_") + [None])[:2]

            try:
                destination_path = maps_path.joinpath(MAPS[uid], MAP_SPECIFIERS[specifier] + "." + extension)
            except KeyError:
                print(f"failed to organize {path}!")
                continue

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(destination_path))


if __name__ == '__main__':
    main()
