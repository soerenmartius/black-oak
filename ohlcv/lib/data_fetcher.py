import asyncio
import ccxt.async_support as ccxt
from datetime import datetime
import logging
from lib import io, util
import pandas as pd
import random
import sys
import toml
from typing import Dict, Any, List


class DataFetcher:

    def __init__(self, config_file):
        """ Constructor to set the config

        :param config_file: string
        :return:
        """
        self.config = self.load_config(config_file)
        self.exchange_config = self.config['exchanges']

        self.debug = self.config['settings']['debug']
        self.proxies = self.config['settings']['proxies']

        # set the log level
        log_level = logging.INFO
        if self.debug is True:
            log_level = logging.DEBUG

        logging.basicConfig(
            stream=sys.stdout,
            level=log_level,
            format='[%(levelname)s] %(message)s'
        )

    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """ Loads and parses a toml config file by file_name

        :param config_file:
        :return: config dict
        """
        try:
            config = toml.load(config_file)
            return config

        except (toml.TomlDecodeError, TypeError) as error:
            logging.fatal(error)
            sys.exit(1)

    async def run(self):
        """ Runs the data fetcher

        :return:
        """
        tasks = [self.exchange_builder(exchange_id) for exchange_id in self.exchange_config.keys()]
        await asyncio.wait(tasks)

    async def exchange_builder(self, exchange_id: str):
        """ Initiates the configured exchanges
            and starts fetching the data for each requested symbol and resolution
            toDo: implement rate limits when we don't use proxies

        :param exchange_id:
        :return:
        """

        # instantiate the exchange by id
        exchange = getattr(ccxt, exchange_id)()

        # get config for current exchange
        config = self.exchange_config[exchange_id]

        # debug toggle
        if self.debug is True:
            exchange.verbose = True

        # check if the exchanges exposes OHLCV data
        if exchange.has['fetchOHLCV'] is False:
            logging.fatal(f'The exchange {exchange.id} does not offer an endpoint to fetch OHLVC data')
            await self.close_exchange(exchange)

        # check if the exchange supports all configured resolutions
        for resolution in config['filter_resolutions']:
            if resolution not in exchange.timeframes:
                logging.fatal(f'The configured {resolution} is not supported by {exchange.id}')
                await self.close_exchange(exchange)

        markets = await exchange.load_markets(reload=True)

        # if symbols aren't explicitly set, pull all markets
        if not config['filter_symbols']:
            config['filter_symbols'] = markets

        fetch_data_tasks = []

        # loop through all pairs of the current exchange and add tasks to our executor
        for symbol in config['filter_symbols']:

            # for idx, market in enumerate(markets):
            #     print(market)
            # sys.exit()

            # check if market exists
            # if symbol not in markets:
            #     logging.fatal(f'market {symbol} does not exist on {exchange_id}')
            #     await self.close_exchange(exchange)

            # if resolutions aren't set explicitly, pull all available resolutions
            if not config['filter_resolutions']:
                config['filter_resolutions'] = exchange.timeframes

            # spawn one task per resolution for each exchange
            for resolution in config['filter_resolutions']:
                logging.info(
                    f'Started to fetch data for {symbol} with a resolution of {resolution} from exchange {exchange.id}'
                )

                fetch_data_tasks.append(self.fetch_ohlvc_data(
                    exchange,
                    symbol,
                    resolution,
                    config['since'],
                    config['until'],
                    config['limit'],
                    self.proxies
                ))

        await asyncio.wait(fetch_data_tasks)
        await exchange.close()

    @staticmethod
    async def close_exchange(exchange: ccxt.Exchange):
        """ Closes the exchange connection and exits the program with status code 1

        :param exchange:
        :return:
        """
        await exchange.close()
        sys.exit(1)

    @staticmethod
    async def fetch_ohlvc_data(
            exchange,
            symbol: str,
            resolution: int,
            since: str,
            until: str,
            limit: int,
            proxies: List[str]
    ):
        """ Fetches the OHLCV candles in batches

        :param exchange: the exchange to fetch the data for
        :param symbol: the symbol to fetch the data for
        :param resolution: the resolution of the OHLCV data
        :param since: start date
        :param until: end date
        :param limit: how many data points to fetch in one call
        :param proxies: a list of proxies to rotate through
        :return: writes the ohlcv time series to the persistence adapter
        """

        # convert datetime strings to timestamp in milliseconds
        since = exchange.parse8601(since)
        until = exchange.parse8601(until)

        # filename
        file_name = f"{str(exchange.id).upper()}_{str(symbol).replace('/', '')}_{resolution}.csv"

        # loop until we fetched everything or forever ( if until = 0 )
        while True:

            # if we defined one or more proxies in our config we'd like to use a random one for this specific exchange
            if len(proxies):
                # if the proxy accepts a session id, set a new one per request
                exchange.aiohttp_proxy = str(random.choice(proxies)).replace('{rand}', util.id_generator())
                exchange.headers = {'Connection': 'close'}

            # exit the loop if we fetched the whole time series
            if since > until and until:
                break

            try:
                logging.info(
                    'Start fetching %s data points from %s for %s and timestamp %s (%s)',
                    limit,
                    exchange.id,
                    symbol,
                    since,
                    datetime.utcfromtimestamp(util.ms_timestamp_to_epoch_timestamp(since))
                )

                params = {'symbol': f'{symbol}'}
                print(params)

                ohlcv_ts = pd.DataFrame(
                    data=await exchange.fetch_ohlcv(
                        'BTC/USD',
                        resolution,
                        since,
                        limit,
                        params
                    ),
                    columns=util.ohlcv_columns(),
                )
                logging.info(f'Received {len(ohlcv_ts.index)} data points')
            except ValueError as error:
                logging.fatal(error)
                sys.exit(1)

            except (
                ccxt.ExchangeError,
                ccxt.AuthenticationError,
                ccxt.ExchangeNotAvailable,
                ccxt.RequestTimeout,
                ccxt.DDoSProtection
            ) as error:
                logging.error(
                    f'Got an error {type(error).__name__} {error.args}. Will try to send the same Request again.'
                )
                # skip current iteration and try again if we run into an exception
                continue

            # write data frame to csv
            io.write_csv(
                f'data/{file_name}',
                ohlcv_ts,
                index=False,
                mode='a'
            )

            # calculate time between the two last candles ( resolution of one candle in ms )
            # and set the timestamp of the next candle so we have it in place for the next request
            resolution_ms = util.detect_resolution(
                datetime.utcfromtimestamp(util.ms_timestamp_to_epoch_timestamp(int(ohlcv_ts['datetime'].iloc[-1]))),
                datetime.utcfromtimestamp(util.ms_timestamp_to_epoch_timestamp(int(ohlcv_ts['datetime'].iloc[-2])))
            )

            # update since
            since = int(ohlcv_ts['datetime'].iloc[-1]) + resolution_ms

            # sleep until the current candle closes if we want to fetch ongoing
            # toDo this needs to be redone
            # if since > util.current_timestamp_in_milliseconds() and until is 0:
            #     logging.info(
            #         '%s-%s-%s Waiting for %s seconds until the next candle closes',
            #         exchange.id,
            #         resolution,
            #         symbol,
            #         since - util.ms_timestamp_to_epoch_timestamp(util.current_timestamp_in_milliseconds())
            #     )
            #     await asyncio.sleep(since - util.current_timestamp_in_milliseconds())
