from datetime import datetime
from lib import util
import pandas as pd
from typing import List


def read_csv(file: str, delimiter: str, col_names: List[str]) -> pd.DataFrame:
    """ Reads a OHLCV time series from csv file

    :param file: the file to read from
    :param delimiter: delimiter for separating the values
    :param col_names: colume names ( headers )
    :return: A data frame containing an OHLCV time series
    """
    ts = pd.read_csv(
        file,
        sep=delimiter,
        names=col_names,
        parse_dates=['datetime'],
        date_parser=lambda x: datetime.utcfromtimestamp(util.ms_timestamp_to_epoch_timestamp(int(x))),
        index_col='datetime',
        float_precision='round_trip',
        engine='c'
    )
    return ts


def write_csv(
        file: str,
        ts: pd.DataFrame,
        delimiter: str = ',',
        na_value: float = float('NaN'),
        headers: bool = False,
        index: bool = True,
        mode: str = 'w',
        encoding: str = 'utf-8'):
    """ Writes a OHLCV time series to a csv file

    :param file: the file to write to
    :param ts: data frame to be written
    :param delimiter: delimiter for separating the values
    :param na_value: Inserted values for missing data
    :param headers: add headers TRUE/FALSE
    :param index: add index TRUE/FALSE
    :param mode: write mode (write, append)
    :param encoding: encoding
    :return:
    """
    ts.to_csv(
        file,
        sep=delimiter,
        na_rep=na_value,
        header=headers,
        index=index,
        mode=mode,
        encoding=encoding
    )
