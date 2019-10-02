import click
from colorama import init, Fore
import glob
import numpy as np
from lib import util, io
from os import path as p
from pandas.io.common import EmptyDataError
import logging
import sys

logging.basicConfig(stream=sys.stdout)
init(autoreset=True)


@click.command()
@click.argument(
    'path',
    type=click.Path(
        exists=True,
        readable=True,
        writable=True
    )
)
@click.option(
    '--delimiter',
    '-d',
    default=',',
    help='Delimiter used to separate values (default: \',\')'
)
@click.option(
    '--resolution',
    '-r',
    type=click.Choice([
        'second',
        'minute',
        'hourly',
        'daily',
    ]),
    default=None,
    help='OHLCV resolution (will be detected automatically if not set explicitly)'
)
@click.option(
    '--write-headers',
    '-wh',
    is_flag=True,
    default=False,
    help='Write headers to file (default: False)'
)
@click.option(
    '--na-value',
    '-nv',
    default=float('NaN'),
    help='Value to be inserted for missing data points (default: \'nan\')'
)
@click.option(
    '--write-file',
    '-w',
    is_flag=True,
    help='Write corrected time series to file'
         '(write to the original file unless you specify a different file using --out)'
)
@click.option(
    '--new-file',
    '-n',
    is_flag=True,
    help='Writes repaired time series to new file (FILE_REPAIRED)'
)
def data_integrity_test(path, delimiter, resolution, write_headers, na_value, write_file, new_file):
    """ This Tool checks a file for integrity. It will loop through all lines and
        check if the time intervals between the candles are consistent.
    """

    files = []
    if p.isdir(path):
        files.extend(glob.glob(path + '*'))
        print(f'Given path {click.format_filename(path)} is a directory. Found {len(files)} files.\n')
    elif p.isfile(path):
        files.append(path)
    else:
        print('Given path is is a special file (socket, FIFO, device file). Functionality not implemented yet!')
        sys.exit(1)

    for file in files:
        file = click.format_filename(file)
        print(f'Loading file: {file}')
        # load file to data frame
        try:
            ohlcv_ts = io.read_csv(
                file,
                delimiter,
                util.ohlcv_columns()
            )
            ohlcv_ts_raw_length = len(ohlcv_ts.index)

        except EmptyDataError:
            # early exit if the file is empty
            print(f'{Fore.RED}No rows found. File seems to be empty.\n')
            continue

        # early exit if the file contains less than two rows
        if len(ohlcv_ts) < 2:
            print(f'{Fore.RED}No or less than 2 rows found. File seems to be empty.\n')
            continue

        print(f'Found {ohlcv_ts_raw_length} data points')
        print(f'Date of first data point {ohlcv_ts.first_valid_index()}')
        print(f'Date of last data point {ohlcv_ts.last_valid_index()}')

        # set or detect resolution
        # toDo: use median or pandas frequency
        if resolution is None:
            resolution_ms = util.detect_resolution(
                ohlcv_ts.index[-1],
                ohlcv_ts.index[-2]
            )
        else:
            resolution_ms = util.string_resolution_to_ms(resolution)

        print(f'Detected resolution: {util.human_readable_resolution(resolution_ms)} ({resolution_ms} milliseconds)')

        # Correct and fill missing data points
        ohlcv_ts = ohlcv_ts.asfreq(freq=str(resolution_ms) + 'ms')
        ohlcv_ts_fixed_length = len(ohlcv_ts.index)

        print(f'Found {ohlcv_ts_fixed_length - ohlcv_ts_raw_length} missing data points '
              f'({util.percentage(ohlcv_ts_fixed_length - ohlcv_ts_raw_length, ohlcv_ts_fixed_length)}% of the data is missing)')

        # convert datetime back to timestamp in ms
        ohlcv_ts.index = (ohlcv_ts.index.astype(np.int64) // 10 ** 6)

        # write data frame to file if flag is set
        if write_file:
            # set file to output file if set
            if new_file:
                file = file + '_REPAIRED'

            io.write_csv(
                file=file,
                ts=ohlcv_ts,
                delimiter=delimiter,
                na_value=na_value,
                headers=write_headers
            )

            print(f'{Fore.GREEN}{ohlcv_ts_fixed_length} data points successfully written to {file}')
        print('\n')


if __name__ == '__main__':
    data_integrity_test()
