import asyncio
import re
from configparser import ConfigParser
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent
config: ConfigParser = ConfigParser(interpolation=None)
config.read(Path(ROOT_FOLDER, "config.ini"), encoding="utf-8")

GENERAL = config["General"]

PATH_TO_SOURCES: Path = Path(ROOT_FOLDER, 'sources')
if not PATH_TO_SOURCES.exists():
    PATH_TO_SOURCES.mkdir()

PROXIES_PATH: Path = Path(GENERAL.get("SavePath", ""))
if not PROXIES_PATH.exists():
    PROXIES_PATH.mkdir()


NOT_CHECKED_PROXIES_FILE = Path(PROXIES_PATH, 'unchecked_proxies.txt')
CHECKED_PROXIES_FILE = Path(PROXIES_PATH, 'parsed.txt')


MAX_CONNECTIONS: int = GENERAL.getint("MaxConnections", '1000')
TIMEOUT: int = GENERAL.getint('Timeout', '10')
INF_MAIN_TIMEOUT_SECONDS: int = GENERAL.getint('MainTimeout', '240')
DEPTH = GENERAL.getint('ParsingDepth', '7')

SEMAPHORE = asyncio.Semaphore(MAX_CONNECTIONS)
REGEX_PATTERN: re.Pattern = re.compile(
    r"(?:^|\D)?(("
    + r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 1-255
    + r"\."
    + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
    + r"\."
    + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
    + r"\."
    + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 0-255
    + r"):"
    + (
            r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
            + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
    )  # 0-65535
    + r")(?:\D|$)"
)


SEARCH_QUERIES = [
    {'searching_query': 'path:http_proxies.txt', 'file_name': 'http.txt'},
    {'searching_query': 'path:proxies.txt', 'file_name': 'http.txt'},
    {'searching_query': 'path:https_proxies.txt', 'file_name': 'https.txt'},
    {'searching_query': 'path:socks5_proxies.txt', 'file_name': 'socks5.txt'},
    {'searching_query': 'path:socks4_proxies.txt', 'file_name': 'socks4.txt'},
]
