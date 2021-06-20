import os
import datetime
import re
import string
import time
from typing import Iterator, Iterable
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValorantLogMessage:
    """Contains parsed data from a log message."""

    timestamp: datetime.datetime
    number: int
    text: str

    @classmethod
    def parse(cls, timestamp: str, number: str, text: str) -> "ValorantLogMessage":
        """Deserialize the fields of the message."""

        return ValorantLogMessage(
            timestamp=datetime.datetime.strptime(timestamp, "%Y.%m.%d-%H.%M.%S:%f"),
            number=int(number),
            text=text)

    def matches(self, terms: Iterable[str]) -> bool:
        """Check if a message matches a set of filter terms."""

        for term in terms:
            if term in self.text:
                return True
        return False

    def __str__(self):
        """Format for printing."""

        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        return f"{timestamp} {self.text}"


message_prefix_pattern = re.compile(r"\[(\d{4}.\d{2}.\d{2}-\d{2}.\d{2}.\d{2}.\d{3})]\[\s*(\d+)](.+)")
printable_characters = set(string.printable)


def _strip_unprintable(line: str) -> str:
    """Strip until we find an ascii character."""

    for i in range(len(line)):
        if line[i] in printable_characters:
            return line[i:]
    return ""


class ValorantLogParser:
    """State machine for handling multiline logging."""

    def __init__(self):
        """Initialize a new parser on empty state."""

        self._buffer = None  # Line buffer
        self._cursor = None  # Current message buffer

    def consume(self, text: str, flush: bool = True) -> Iterator[ValorantLogMessage]:
        """Consume some amount of text, add messages to self queue."""

        # Prepend any trailing data from the last consume to text
        if self._buffer is not None:
            text = self._buffer + text
            self._buffer = None

        # Iterate through the lines in our text chunk
        for line in text.splitlines(keepends=True):

            # Do some minor processing, add the line to buffer and break if no final newline
            line = _strip_unprintable(line)
            if not line.endswith("\n"):
                self._buffer = line
                break

            # Try to match our log format
            message_prefix_match = message_prefix_pattern.match(line)

            # If we got a match, we can flush the prior message since we know it's definitely complete
            if message_prefix_match is not None:
                if self._cursor is not None:
                    yield self._cursor

                # Also start the new message for the line we found
                self._cursor = ValorantLogMessage.parse(*message_prefix_match.groups())

            # If there was no match, it's random data; try to append it to the message in the buffer
            elif self._cursor is not None:
                self._cursor.text += line

            # Otherwise we found some rogue data, probably at the top of the file
            else:
                raise print(f"skipped data: {line.rstrip()}")

        # Yield the message in our buffer if we're forcing flush
        if flush:
            self.flush()

    def flush(self):
        """Release any leftover message."""

        if self._cursor is not None:
            yield self._cursor
            self._cursor = None


class ValorantLog:
    """Parses messages that can span multiple lines."""

    path: Path

    DEFAULT_PATH = Path(os.getenv("LOCALAPPDATA"), "VALORANT", "Saved", "Logs", "ShooterGame.log")
    READ_CHUNK_SIZE = 4096

    def __init__(self, path: Path):
        """Initialize a new log with its file system path."""

        self.path = path

    def read(self) -> Iterator[ValorantLogMessage]:
        """Iterate existing lines in the file. Skips garbage at top."""

        parser = ValorantLogParser()
        with self.path.open() as file:
            while True:
                chunk = file.read(ValorantLog.READ_CHUNK_SIZE)
                yield from parser.consume(chunk)
                if len(chunk) < ValorantLog.READ_CHUNK_SIZE:
                    break

    def watch(self, interval: float = 1) -> Iterator[ValorantLogMessage]:
        """Watch the tail of the file for new log messages."""

        parser = ValorantLogParser()
        with self.path.open() as file:
            file.seek(0, os.SEEK_END)
            while True:
                yield from parser.consume(file.read(), flush=True)
                time.sleep(interval)


def main():
    """Create an argument parser, run based on parsed args."""

    import argparse

    parser = argparse.ArgumentParser(description="a Valorant game log parser and watcher")
    parser.add_argument(
        "-p", "--path",
        action="store",
        help="alternate path for Valorant log file",
        default=ValorantLog.DEFAULT_PATH)
    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        help="watch for updates to the log file")
    parser.add_argument(
        "-f", "--filter",
        action="store",
        nargs="+",
        help="filter for text")
    args = parser.parse_args()

    log = ValorantLog(args.path)

    for message in log.read():
        if args.filter is None or message.matches(args.filter):
            print(message)

    if args.watch:
        try:
            for message in log.watch():
                if args.filter is None or message.matches(args.filter):
                    print(message)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
