# Logger

This tool was originally developed by [Hamper](https://github.com/OwOHamper).
The logger provides access to the Valorant game log file; by default, it prints out the existing contents.
Optionally, you can also watch the file for updates or filter all printed messages by substring search.

# Examples

To print through existing messages in the Valorant log file, simply run the logger with no arguments:

```commandline
$ python3.9 logger.py
```

To watch the tail end of the log file for updates (while the game is running), use `--watch`:

```commandline
$ python3.9 logger.py --watch
```

To filter messages printed by substring search, use `--filter`.
For example, if you wanted to search for all messages that included a URL:

```commandline
$ python3.9 logger.py --watch --filter "https://"
```
