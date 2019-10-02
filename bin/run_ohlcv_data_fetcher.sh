#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 ${DIR}/../ohlcv/fetch_ohlcv_data.py ${DIR}/../config.toml
