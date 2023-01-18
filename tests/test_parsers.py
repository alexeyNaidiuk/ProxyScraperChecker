from pathlib import Path
from typing import Generator
from unittest import TestCase

from proxy_parser.config import PATH_TO_SOURCES
from proxy_parser.parsers import get_files_from_folder, get_proxies_from_link, get_links_from_file, \
    get_sources_from_github

TEST_PROXIES_SOURCE = 'https://github.com/Supergamerrr/rqeqqwe/blob/f138393a9a41429a5f5e7fab8dfeaf726a386c40/required/http-proxies.txt'


class TestParsers(TestCase):

    def test_get_list_of_files_with_sources(self):
        '''
        получаем список всех файлов с источниками проксей

        '''

        list_of_files: tuple = get_files_from_folder(PATH_TO_SOURCES)
        self.assertIn(Path(PATH_TO_SOURCES, 'http.txt'), list_of_files)
        self.assertIn(Path(PATH_TO_SOURCES, 'socks4.txt'), list_of_files)
        self.assertIn(Path(PATH_TO_SOURCES, 'socks5.txt'), list_of_files)

    def test_get_links_from_text_file(self):
        '''
        получаем источники проксей из файлов и проверяем что это ссылки

        '''

        list_of_files: tuple = get_files_from_folder(PATH_TO_SOURCES)

        for file in list_of_files:
            sources: tuple = get_links_from_file(Path(PATH_TO_SOURCES, file))
            for source in sources:
                self.assertIn('http', source)

    def test_get_proxy_from_link(self):
        '''
        получаем список проксей из источника

        '''

        proxies: tuple = get_proxies_from_link(TEST_PROXIES_SOURCE)
        for p in proxies:
            self.assertIn(':', p)

    def test_get_proxy_sources_from_github(self):
        '''
        получаем источники прокси с гитхаб

        '''

        github_parser: Generator = get_sources_from_github(depth=1)  # generator of str

        for link in github_parser:
            self.assertIn('github', link)
