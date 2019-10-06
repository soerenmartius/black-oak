import datetime

import asyncio
import click
from lib.data_fetcher import DataFetcher

# available future symbols
futures = {
    'ADA': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'BCH': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'EOS': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'ETH': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'LTC': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'TRX': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'XBT': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
    'XRP': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 18},
}


# F = January
# G = February
# H = March
# J = April
# K = May
# M = June
# N = July
# Q = August
# U = September
# V = October
# X = November
# Z = December
month_codes = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']


@click.command()
@click.argument(
    'config',
    type=click.Path(
        exists=True,
        readable=True,
    )
)
def pull_bitmex_futures(config):
    config = get_futures_config(config)

    data_fetcher = DataFetcher(config)
    loop = asyncio.get_event_loop()

    # wait for all tasks to be finished
    loop.run_until_complete(data_fetcher.run())


def get_futures_config(config):
    for symbol, futures_config in futures.items():

        # current year as two digits
        current_year = int(datetime.datetime.now().strftime('%y'))
        start_year = futures_config['since_year']

        while start_year <= current_year:

            for month in month_codes:
                print(f'{symbol}{month}{start_year}')

            # set iteration to next year
            start_year = start_year + 1


if __name__ == '__main__':
    pull_bitmex_futures()
