import asyncio
import itertools
import os
from pathlib import Path
from typing import NoReturn, Any, AsyncGenerator

import aiohttp
import requests
from bs4 import BeautifulSoup

from proxy_parser import checkers
from proxy_parser.config import REGEX_PATTERN, SEARCH_QUERIES, PATH_TO_SOURCES, DEPTH, NOT_CHECKED_PROXIES_FILE, \
    SEMAPHORE, CHECKED_PROXIES_FILE

COOKIES = {
    '_octo': 'GH1.1.2045407306.1670336220',
    '_device_id': '4080764a6f93b98d37a7aba816e05ad3',
    'user_session': 'GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh',
    '__Host-user_session_same_site': 'GJ2FquNK2R7LQszFIYzptfpN0wfc8zUgOEk89qHJoPXfzcKh',
    'logged_in': 'yes',
    'dotcom_user': 'adw3r',
    'color_mode': '%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark_dimmed%22%2C%22color_mode%22%3A%22dark%22%7D%7D',
    'preferred_color_mode': 'dark',
    'tz': 'Europe%2FKiev',
    'has_recent_activity': '1',
    '_gh_sess': 'q7aH3Q2vx6NV1WTTA0MFUcTzyhObT0evWl5c6LDusWpknBgE5%2B7fUN%2Fot6SUptY9n%2BoPiaXP694p1FIa2FGtOH1Mspzxzjm2bO0xvJDFd3e3jDab2I%2B42HrIBlZ3ZaINaok%2B9pIJuKxfi0U4PEjBuGB4HR764mOpc7glON1NrJ%2FFbXk%2Bn%2FFJWYvRheKTeeotpS7qIGb2sd91zheolHgHgiIJU9R%2FUJlSm20p0dM7TvGx9Vh0NlWRPBMLbfzc6PCV7KnibmO45YF7VAjyzD0OjuVzpMwYcGLvTdMRYY4Xe1SkIOlpJOsHD%2BkyZMFCE3Kc9VmKn%2B%2BXDXRvYAZpmg%3D%3D--Mv%2Bp%2FNXaXIsdeTAY--ZwQfQks6oKqHZvK%2BrkwHsQ%3D%3D',
}
HEADERS = {
    'authority': 'github.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"3d35da3768d73690629a327321ba5cf3"',
    'referer': 'https://github.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


async def fetch_source(session, source_link) -> tuple[str | Any, ...] | None:
    text = None
    proxies = tuple()
    try:
        async with SEMAPHORE:
            async with session.get(source_link) as response:
                text = await response.text()
    except Exception as e:
        print(e)
    if text:
        proxies = tuple(set(proxy.group(1) for proxy in set(REGEX_PATTERN.finditer(text))))
    return proxies


async def get_proxies(sources_urls: tuple[str]) -> tuple[str]:
    async with aiohttp.ClientSession() as session:
        cors = [fetch_source(session, url) for url in sources_urls]
        proxies: tuple[str] = await asyncio.gather(*cors)
        return proxies


def clear_file(path_to_file):
    with open(path_to_file, 'w') as f:
        f.write('')


def append_to_file(path_to_file, item: str):
    with open(path_to_file, 'a') as file:
        file.write(f'{item}\n')


def append_iterable_to_file(path_to_file: Path, iterable: set):
    with open(path_to_file, 'a') as file:
        for line in iterable:
            file.write(f'\n{line}')


def get_sources_from_github(page: int = 10, query: str = 'filename:proxies.txt') -> requests.Response | None:
    params = {
        'p': page,
        # 'o': 'desc',
        'q': query,
        # 's': 'indexed',
        'type': 'code',
    }
    try:
        response = requests.get('https://github.com/search', params=params, cookies=COOKIES, headers=HEADERS,
                                timeout=10)
        return response if response.ok else None
    except Exception as e:
        import logging
        logging.exception(e)
        return None


def parse_response(response_text: str) -> list[str]:
    soup = BeautifulSoup(response_text, 'lxml')
    all_a = soup.find_all('a', {'data-testid': 'link-to-search-result'})
    return [f'https://github.com{a.get("href")}' for a in all_a]


def clean_file_from_duplicates(path_to_file: Path | str) -> NoReturn:
    with open(path_to_file) as file:
        iterable = set(file.read().split('\n'))
        if '' in iterable:
            iterable.remove('')
    with open(path_to_file, 'w') as file:
        file.write('\n'.join(iterable))


def get_files_from_folder(path_to_folder: Path | str) -> tuple[Path]:
    return tuple(Path(path_to_folder, str(file)) for file in os.listdir(path_to_folder))


def get_links_from_file(path_to_file: Path | str) -> tuple[str]:
    clean_file_from_duplicates(path_to_file)
    with open(path_to_file) as file:
        return tuple(set(file.read().split('\n')))


def get_sources_dict(sources_list: tuple[Path]) -> dict[str, tuple]:
    sources_dict = {}
    for source_file in sources_list:
        source_name = source_file.name.removesuffix('.txt')
        sources_dict[source_name] = tuple(link for link in get_links_from_file(source_file))
    return sources_dict


async def update_sources():
    for query in SEARCH_QUERIES:
        print(f'searching for {query}')
        path_to_source = Path(PATH_TO_SOURCES, query['file_name'])
        links = []
        for page in range(DEPTH):
            response: requests.Response | None = get_sources_from_github(page, query['searching_query'])
            if not response:
                continue
            links_from_github = parse_response(response.text)
            if links_from_github:
                links.extend(links_from_github)
        print(*links, sep='\n')
        append_iterable_to_file(path_to_source, set(links))
        clean_file_from_duplicates(path_to_source)


async def parse_unchecked_proxies():
    sources_list: tuple[Path] = get_files_from_folder(PATH_TO_SOURCES)
    sources_dict: dict[str, tuple] = get_sources_dict(sources_list)
    unchecked_proxies_set = set()
    for protocol, urls in sources_dict.items():
        proxies: tuple[str] = await get_proxies(urls)
        if proxies:
            proxies: set[str] = set(itertools.chain.from_iterable([p for p in proxies if p]))
            print(proxies)
            unchecked_proxies_set.update(set(f'{protocol}://{proxy}' for proxy in proxies))
    with open(NOT_CHECKED_PROXIES_FILE, 'w') as file:
        file.write('\n'.join(unchecked_proxies_set))
    print('finished to collect proxies')


async def check_proxies():
    unchecked_proxies_set = await get_uncheked_proxies()
    checked_proxies_generator: AsyncGenerator = checkers.check_proxies_generator(unchecked_proxies_set)
    clear_file(CHECKED_PROXIES_FILE)
    async for proxy, json_resp in checked_proxies_generator:
        print(proxy, json_resp)
        append_to_file(CHECKED_PROXIES_FILE, proxy)


async def get_uncheked_proxies() -> set[str]:
    with open(NOT_CHECKED_PROXIES_FILE) as file:
        return set(file.read().strip().split('\n'))
