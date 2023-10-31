import asyncio
import datetime

from proxy_parser import config, parsers


async def main():
    await parsers.update_sources()
    await parsers.parse_unchecked_proxies()
    await parsers.check_proxies()


async def infinite_main():
    while True:
        print('started parsing!')
        await main()
        awaking_time = datetime.datetime.now() + datetime.timedelta(seconds=config.INF_MAIN_TIMEOUT_SECONDS)
        print(f'parsing will start at {awaking_time}!')
        await asyncio.sleep(config.INF_MAIN_TIMEOUT_SECONDS)


if __name__ == '__main__':
    asyncio.run(infinite_main())
