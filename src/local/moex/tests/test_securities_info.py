from pathlib import Path

import pandas as pd
import pytest

import settings
from local.moex.iss_securities_info import aliases, securities_info, SecuritiesInfoDataManager, lot_size
from web.labels import LOT_SIZE, COMPANY_NAME, REG_NUMBER


@pytest.fixture(scope='module', autouse=True)
def make_temp_dir(tmpdir_factory):
    saved_path = settings.DATA_PATH
    temp_dir = tmpdir_factory.mktemp('securities_info')
    settings.DATA_PATH = Path(temp_dir)
    yield
    settings.DATA_PATH = saved_path


def test_first_time_security_info():
    df = securities_info(('KBTK', 'MOEX'))
    assert len(df.index) == 2
    assert df.loc['KBTK', COMPANY_NAME] == 'КузбТК ао'
    assert df.loc['MOEX', REG_NUMBER] == '1-05-08443-H'
    assert df.loc['KBTK', LOT_SIZE] == 10


def test_all_tickers_in_local_data_security_info():
    df = securities_info(('MOEX',))
    assert len(df.index) == 1
    assert df.loc['MOEX', COMPANY_NAME] == 'МосБиржа'
    assert df.loc['MOEX', REG_NUMBER] == '1-05-08443-H'
    assert df.loc['MOEX', LOT_SIZE] == 10


def test_not_all_tickers_in_local_data_security_info():
    df = securities_info(('MTSS', 'MOEX'))
    assert len(df.index) == 2
    assert df.loc['MTSS', COMPANY_NAME] == 'МТС-ао'
    assert df.loc['MOEX', REG_NUMBER] == '1-05-08443-H'
    assert df.loc['MTSS', LOT_SIZE] == 10


def test_all_tickers_are_new_security_info():
    df = securities_info(('SNGSP', 'GAZP'))
    assert len(df.index) == 2
    assert df.loc['SNGSP', COMPANY_NAME] == 'Сургнфгз-п'
    assert df.loc['GAZP', REG_NUMBER] == '1-02-00028-A'
    assert df.loc['SNGSP', LOT_SIZE] == 100


def test_aliases():
    assert aliases('UPRO') == ('UPRO', 'EONR', 'OGK4')


def test_download_update():
    with pytest.raises(NotImplementedError):
        SecuritiesInfoDataManager().download_update()


def test_lot_size():
    df = lot_size(('AKRN', 'SNGSP', 'KBTK'))
    assert isinstance(df, pd.Series)
    assert df.shape == (3,)
    assert df['AKRN'] == 1
    assert df['SNGSP'] == 100
    assert df['KBTK'] == 10
