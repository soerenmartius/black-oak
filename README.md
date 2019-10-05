# Black Oak 

[![Build Status](https://travis-ci.org/soerenmartius/black-oak.svg?branch=master)](https://travis-ci.org/soerenmartius/black-oak)
[![Known Vulnerabilities](https://snyk.io//test/github/soerenmartius/black-oak/badge.svg?targetFile=requirements.txt)](https://snyk.io//test/github/soerenmartius/black-oak?targetFile=requirements.txt)
[![Maintainability](https://api.codeclimate.com/v1/badges/ca28e22f618d3fbdc4ae/maintainability)](https://codeclimate.com/github/soerenmartius/black-oak/maintainability)
[![MIT License](https://badges.frapsoft.com/os/mit/mit.svg?v=102)](https://github.com/ellerbrock/open-source-badge/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fsoerenmartius%2Fblack-oak.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fsoerenmartius%2Fblack-oak?ref=badge_shield)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)



A Service to pull and validate OHLCV Data from various Crypto Exchanges using [Python](https://www.python.org/) and [CCXT](https://github.com/ccxt/ccxt).

![Black Oak Image](https://cdn11.bigcommerce.com/s-f74ff/products/9570/images/23270/bbbbbbbbbbbbbbbb__41098.1483834378.1280.1280.jpg?c=2)


### Disclaimer:
Black Oak uses the [ccxt library](https://github.com/ccxt/ccxt) which is a collection of available crypto exchanges or
exchange classes. Please note that some exchanges don't offer to pull unlimited historical data. **Some exchanges may
limit the access to historical data to a few months or days only.**

## How to use

### Docker
The recommended to use Black Oak is running it with [Docker](https://www.docker.com).

Runs the docker container and mounts the local `./data` directory of the host system inside the Container. 
```
make docker-run-with-mountpoint
``` 

### Python
Black Oak requires Python 3.7 or higher.

#### Install Requirements
```
pip install -r requirements.txt
```

#### Run Black Oak
```bash
./bin/run_ohlcv_data_fetcher.sh config.toml
```


## Configuration
```
[settings]
# debug output true / false
debug = true

# persistence ( at the moment we only support file, aws kinesis firehose will be implemented later )
persistence = "file"

# a list of proxies to rotate through
# you can use {rand} to append a unique session id for every http request
proxies = [
    "http://username:password@some-proxy.io?session={rand}:22225",
]

# rate limit should be enabled in case you don't use any proxy
ratelimit = false

# this section is the list of exchanges, assets and resolutions to poll
[exchanges]

    [exchanges.bitfinex]
    filter_symbols = [] # passing an empty list will pull all available symbols!!!
    filter_resolutions = []    # passing an empty list will pull all available resolutions
    since = "2017-01-01 00:00:00"
    until = "2019-06-26 00:00:00"
    limit = 5000

    [exchanges.bitmex]
    filter_symbols = ["BTC/USD", "ETH/USD"]
    filter_resolutions = ["1m", "1h", "1d"]
    since = "2017-01-01 00:00:00"
    until = "2019-06-26 00:00:00"
    limit = 750
```

## Proxy
It's recommended to run black-oak with a proxy server such as [luminati.io](https://luminati.io) to work around the exchange's rate limits.

## Data Integrity Check
Black Oak comes with a script to check the data integrity of a file. This script will check line by line if the time distance
between the current and the previous candle is accurate. If it isn't, it will return the corrupted items with some
details such as missing number of candles.

The distance in seconds between two candles we can pass with the `--resolution` parameter. It's an optional parameter. If
you don't pass one, the script will take the distance between the first two candles. In general, we advise you to pass the 
resolution


Usage:
```bash
./bin/check_data_integrity.sh --help
```
![Data Integrity Check](_docs/_images/usage.png)

Run the integrity checks and write result
```bash
# check a single file and write to BINANCE_LTCUSDT_1h_REPAIRED
./bin/check_data_integrity.sh data/BINANCE_LTCUSDT_1h -w -o BINANCE_LTCUSDT_1h_COMPLETE 

# check the file and explicitly set the resolution to minutes
./bin/check_data_integrity.sh data/BINANCE_LTCUSDT_1h -r minute

# check a single file and write to the same file
./bin/check_data_integrity.sh data/BINANCE_LTCUSDT_1h -w

# checks a directory of files and writes to new files (FILE_REPAIRED)
./bin/check_data_integrity.sh data/ -wn

# checks a directory of files and writes to new files (FILE_REPAIRED) and saves the test report to the file test_report.txt
./bin/check_data_integrity.sh data/ -wn > test_report.txt

# checks a directory of files and writes to new files (FILE_REPAIRED) and redirects the output to the console and  file  
./bin/check_data_integrity.sh data/ -wn >&1 | tee test_report.txt
```


