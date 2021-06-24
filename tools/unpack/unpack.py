import requests
import zipfile
import multiprocessing
from PIL import Image

from pathlib import Path
from typing import IO


LATEST_ARCHIVE_URL = "https://valorant.dyn.riotcdn.net/x/content-catalog/PublicContentCatalog-release-03.00.zip"


def download(url: str) -> Path:
    """Download the archive and return its path."""

    response = requests.get(url, stream=True)
    name = url.rsplit("/", maxsplit=1)[-1]
    path = Path(name)

    print(f"downloading {name}...")
    with path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=4096):
            file.write(chunk)
    response.close()

    return path


def mirror(source: IO[bytes], output_path: Path):
    with output_path.open("wb") as file:
        while (chunk := source.read(4096)) != "":
            file.write(chunk)


def change_extension(path: Path, to: str) -> Path:
    return path.parent.joinpath(path.parts[-1].rsplit(".", maxsplit=1)[0] + "." + to)


def convert_image(source: IO[bytes], source_format: str, output_path: Path, output_format: str,):
    image = Image.open(source, formats=(source_format,))
    with output_path.open("wb") as file:
        image.save(file, format=output_format)


def unpack(source_path: str, target_path: str, destination_path: str):
    with zipfile.ZipFile(source_path) as archive:
        with archive.open(target_path, "r") as file:
            output_path = Path(destination_path, target_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.endswith(".tga"):
                output_path = change_extension(output_path, "png")
                convert_image(file, "tga", output_path, "png")
            else:
                mirror(file, output_path)


def main():
    """Run the command line utility."""

    import argparse
    none = object()

    parser = argparse.ArgumentParser()
    source_parser = parser.add_mutually_exclusive_group()
    source_parser.add_argument(
        "-d", "--download",
        nargs="?",
        default=none,
        dest="download",
        help="URL of the asset pack to download")
    source_parser.add_argument(
        "-f", "--file",
        dest="file",
        help="unpack an existing archive")
    parser.add_argument("-p", "--prefix", dest="prefix", nargs="+", help="")

    args = parser.parse_args()

    if args.download is not none:
        url = LATEST_ARCHIVE_URL if args.download is None else args.download
        source_path = download(url)
    else:
        source_path = Path(args.file)

    destination_path = Path("unpacked")
    jobs = []

    print("inspecting archive...")
    with zipfile.ZipFile(source_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if args.prefix is None or any(info.filename.startswith(prefix) for prefix in args.prefix):
                jobs.append((str(source_path.absolute()), info.filename, str(destination_path.absolute())))

    print("starting unpacking pool...")
    with multiprocessing.Pool() as pool:
        pool.starmap(unpack, jobs)


if __name__ == "__main__":
    main()
