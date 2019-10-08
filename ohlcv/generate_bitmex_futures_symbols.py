import datetime

# available future symbols
futures = {
    'ADA': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 17},
    'BCH': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 17},
    'EOS': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 17},
    'ETH': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 16},
    'LTC': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 19},
    'TRX': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 17},
    'XBT': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 15},
    'XRP': {'timeframes': ['1m', '5m', '1h', '1d'], 'since_year': 17},
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

if __name__ == '__main__':
    for symbol, futures_config in futures.items():

        # current year as two digits
        current_year = int(datetime.datetime.now().strftime('%y'))
        start_year = futures_config['since_year']

        while start_year <= current_year:

            for month in month_codes:
                print(f'https://www.bitmex.com/api/v1/trade/bucketed?symbol={symbol}{month}{start_year}&binSize=1d')

            # set iteration to next year
            start_year = start_year + 1
