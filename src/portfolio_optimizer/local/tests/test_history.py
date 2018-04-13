from pathlib import Path

import arrow
import pandas as pd
import pytest

from portfolio_optimizer import web, settings
from portfolio_optimizer.local import local_quotes
from portfolio_optimizer.local.local_quotes import get_prices_history, get_volumes_history
from portfolio_optimizer.local.local_quotes import get_quotes_history, LocalQuotes
from portfolio_optimizer.settings import VOLUME, CLOSE_PRICE


def updated_df():
    saved_date = local_quotes.END_OF_CURRENT_TRADING_DAY
    local_quotes.END_OF_CURRENT_TRADING_DAY = arrow.get().shift(months=1)
    df2 = get_quotes_history('MSTT')
    local_quotes.END_OF_CURRENT_TRADING_DAY = saved_date
    return df2


@pytest.fixture(scope='module', name='dfs', autouse=True)
def make_dfs_and_fake_path(tmpdir_factory):
    saved_path = settings.DATA_PATH
    temp_dir = tmpdir_factory.mktemp('data')
    settings.DATA_PATH = Path(temp_dir)
    dfs = [get_quotes_history('MSTT'), updated_df(), get_quotes_history('MSTT')]
    yield dfs
    settings.DATA_PATH = saved_path


@pytest.fixture(params=range(3), name='df')
def yield_df(request, dfs):
    return dfs[request.param]


def test_get_quotes_history(df):
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 2
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert df.index[0] == pd.to_datetime('2010-11-03')
    assert df.shape[0] > 100
    assert df.loc['2018-03-09', CLOSE_PRICE] == 148.8 and df.loc['2018-03-09', VOLUME] == 2960


def test_validate_last_date_error():
    df_old = LocalQuotes('MSTT')
    df_new = web.quotes('AKRN', df_old.df_last_date)
    with pytest.raises(ValueError) as info:
        df_old._validate_new_data(df_new)
    assert 'Загруженные данные MSTT не стыкуются с локальными.' in str(info.value)


def test_get_volumes_history():
    df = get_volumes_history(['KBTK', 'RTKMP'])
    assert df.loc['2018-03-09', 'KBTK'] == 0
    assert df.loc['2018-03-13', 'RTKMP'] == 400100


def test_get_prices_history():
    df = get_prices_history(['KBTK', 'RTKMP'])
    assert pd.isna(df.loc['2018-03-09', 'KBTK'])
    assert df.loc['2018-03-13', 'RTKMP'] == 62

