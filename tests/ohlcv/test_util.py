from datetime import datetime
from ohlcv.lib import util
import pandas as pd
import pytest
from typing import Dict


class TestUtil(object):

    #########################
    # FIXTURES
    #########################
    @pytest.fixture
    def dataframe_with_three_duplicates(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                [1504350000000, 4634.95, 4688.66, 4617.95, 4630.01, 18.11696],
                [1504353600000, 4669.75, 4675.0, 4516.17, 4604.97, 46.381532],
                [1504357200000, 4604.97, 4637.56, 4569.65, 4618.39, 21.950267],
                [1504360800000, 4618.39, 4618.39, 4418.22, 4483.94, 53.057107],
                [1504364400000, 4433.58, 4483.62, 4354.61, 4460.19, 65.915579],
                [1504368000000, 4465.12, 4508.96, 4377.43, 4439.0, 48.470317],
                [1504371600000, 4443.0, 4545.76, 4377.44, 4530.01, 36.504369],
                [1504375200000, 4554.98, 4554.98, 4480.81, 4486.06, 31.20194],
                [1504386000000, 4351.28, 4414.59, 4286.87, 4299.53, 25.71493],
                [1504389600000, 4398.49, 4492.88, 4299.47, 4405.0, 24.656166],
                [1504389600000, 4398.49, 4492.88, 4299.47, 4405.0, 24.656166],
                [1504389600000, 4398.49, 4492.88, 4299.47, 4405.0, 24.656166],
                [1504393200000, 4439.92, 4508.5, 4392.72, 4472.14, 28.243604],
                [1504396800000, 4508.5, 4618.38, 4508.5, 4600.53, 29.470282],
                [1504400400000, 4556.71, 4609.98, 4486.19, 4560.0, 27.551972],
                [1504404000000, 4545.0, 4569.95, 4467.88, 4568.91, 25.620889],
                [1504407600000, 4568.91, 4618.4, 4555.0, 4569.54, 29.925615],
            ],
            columns=util.ohlcv_columns()
        )

    @pytest.fixture
    def epoch_timestamp(self) -> int:
        # Sat Jun 21 19:10:00 UTC 2014
        return 1403377800

    @pytest.fixture()
    def fixed_2019_string_date(self) -> str:
        return '2019-01-01 01:01:59'

    @pytest.fixture()
    def resolution_list(self) -> Dict[int, str]:
        return {
            '1 Minute': 60000,
            '3 Minutes': 180000,
            '5 Minutes': 300000,
            '10 Minutes': 600000,
            '15 Minutes': 900000,
            '30 Minutes': 1800000,
            '45 Minutes': 2700000,
            '1 Hour': 3600000,
            '2 Hours': 7200000,
            '3 Hours': 10800000,
            '4 Hours': 14400000,
            '6 Hours': 21600000,
            '12 Hour': 43200000,
            '1 Day': 86400000
        }

    #########################
    # UNIT TESTS
    #########################
    def test_detect_resolution(self):
        # Jan 1 2019 00:00 am
        start_date = datetime(2019, 1, 1, 0, 0, 0)

        # Jan 2 2019 01:01 am
        end_date = datetime(2019, 1, 1, 0, 1, 0)

        # 1 min ( 60000 milliseconds )
        assert util.detect_resolution(end_date, start_date) == 60000

    def test_df_duplicates(self, dataframe_with_three_duplicates):
        assert len(util.df_duplicates(dataframe_with_three_duplicates, 'first')) == 2
        assert len(util.df_duplicates(dataframe_with_three_duplicates, 'last')) == 2
        assert len(util.df_duplicates(dataframe_with_three_duplicates, False)) == 3

    def test_epoch_timestamp_to_ms_timestamp(self, epoch_timestamp: int):
        assert util.epoch_timestamp_to_ms_timestamp(epoch_timestamp) == 14033778e5

    def test_ms_timestamp_to_epoch_timestamp(self, epoch_timestamp: int):
        assert util.ms_timestamp_to_epoch_timestamp(
            util.epoch_timestamp_to_ms_timestamp(epoch_timestamp)) == epoch_timestamp

    def test_string_resolution_to_ms(self):
        assert util.string_resolution_to_ms('minute') == 60000
        assert util.string_resolution_to_ms('hourly') == 60000 * 60
        assert util.string_resolution_to_ms('daily') == 60000 * 60 * 24

    def test_string_date_to_ms_timestamp(self, fixed_2019_string_date):
        assert int(util.string_date_to_ms_timestamp(fixed_2019_string_date)) == 1546304519000

    def test_human_readable_resolution(self, resolution_list):
        for resolution_str, resolution_ms in resolution_list.items():
            assert util.human_readable_resolution(resolution_ms) == resolution_str

    def test_percentage(self):
        assert util.percentage(20, 100) == 20
