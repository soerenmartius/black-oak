import asyncio
import click
from lib.data_fetcher import DataFetcher


@click.command()
@click.argument(
    'config',
    type=click.Path(
        exists=True,
        readable=True,
    )
)
def fetch_ohlcv_data(config):
    data_fetcher = DataFetcher(config)
    loop = asyncio.get_event_loop()

    # wait for all tasks to be finished
    loop.run_until_complete(data_fetcher.run())


if __name__ == '__main__':
    fetch_ohlcv_data()
