import datetime
import urllib.error

import pytest

from portfolio_optimizer.web.web_dividends import dividends, make_url


def test_url():
    assert make_url('MOEX') == 'http://www.dohod.ru/ik/analytics/dividend/moex'


def test_wrong_url():
    with pytest.raises(urllib.error.URLError) as info:
        dividends('TEST')
    url = make_url('TEST')
    assert f'Неверный url: {url}' in str(info.value)


def test_get_dividends():
    df = dividends('VSMO')
    assert df.loc[datetime.date(2017, 10, 19)] == 762.68
    assert df.loc[datetime.date(2004, 3, 29)] == 11


def test_no_dividends_table_in_html():
    with pytest.raises(IndexError) as error:
        dividends('MSRS')
    assert 'нет таблицы с дивидендами.' in str(error.value)