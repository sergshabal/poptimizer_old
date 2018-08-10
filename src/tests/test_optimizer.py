import pytest

import optimizer
import portfolio
from optimizer import Optimizer
from portfolio import Portfolio
from settings import AFTER_TAX


@pytest.fixture(scope='module', name='opt')
def case_optimizer():
    pos = dict(AKRN=679,
               BANEP=392,
               CHMF=173,
               GMKN=139,
               LKOH=123,
               LSNGP=59,
               LSRG=1341,
               MSRS=38,
               MSTT=2181,
               MTSS=1264,
               MVID=141,
               PMSBP=2715,
               RTKMP=1674,
               SNGSP=263,
               TTLK=234,
               UPRO=1272,
               VSMO=101)
    port = Portfolio(date='2018-07-24',
                     cash=102_262,
                     positions=pos)
    save_max_trade = optimizer.MAX_TRADE
    save_cut_off = portfolio.VOLUME_CUT_OFF
    optimizer.MAX_TRADE = 0.006
    portfolio.VOLUME_CUT_OFF = 2.9 * optimizer.MAX_TRADE
    opt = Optimizer(port)
    yield opt
    optimizer.MAX_TRADE = save_max_trade
    portfolio.VOLUME_CUT_OFF = save_cut_off


def test_dividends_gradient_growth(opt):
    gradient_growth = opt.dividends_gradient_growth
    assert gradient_growth['MSTT'] == pytest.approx(0.0150399027409569 * AFTER_TAX)
    assert gradient_growth['MSRS'] == pytest.approx(0.0060346499492693 * AFTER_TAX)
    assert gradient_growth['RTKMP'] == pytest.approx(0.0 * AFTER_TAX)
    assert gradient_growth['LSNGP'] == pytest.approx(0.0129893484990373 * AFTER_TAX)
    assert gradient_growth['LKOH'] == pytest.approx(0.0 * AFTER_TAX)
    assert gradient_growth['PMSBP'] == pytest.approx(0.0 * AFTER_TAX)
    assert gradient_growth['CHMF'] == pytest.approx(0.0 * AFTER_TAX)
    assert gradient_growth['GMKN'] == pytest.approx(0.0 * AFTER_TAX)


def test_drawdown_gradient_growth(opt):
    gradient_growth = opt.drawdown_gradient_growth
    assert gradient_growth['MSTT'] == pytest.approx(0.400990435348472)
    assert gradient_growth['MSRS'] == pytest.approx(0.0332297448249415)
    assert gradient_growth['RTKMP'] == pytest.approx(0.0)
    assert gradient_growth['LSNGP'] == pytest.approx(0.0517992767361088)
    assert gradient_growth['LKOH'] == pytest.approx(0.0)
    assert gradient_growth['PMSBP'] == pytest.approx(0.0)
    assert gradient_growth['CHMF'] == pytest.approx(0.0)
    assert gradient_growth['GMKN'] == pytest.approx(0.0)


def test_dominated(opt):
    dominated = opt.dominated
    assert dominated['UPRO'] == 'VSMO'
    assert dominated['LSRG'] == ''
    assert dominated['VSMO'] == ''
    assert dominated['SNGSP'] == 'CHMF'


def test_t_dividends_growth(opt):
    assert opt.t_dividends_growth == pytest.approx(0.613956329529872)


def test_t_drawdown_growth(opt):
    assert opt.t_drawdown_growth == pytest.approx(2.17621763863156)


def test_best_trade(opt):
    best_string = opt._str_best_trade()
    assert 'Продать MSTT - 5 сделок по 19 лотов' in best_string
    assert 'Купить LSRG - 5 сделок по 26 лотов' in best_string


def test_str_t_score_10(opt, monkeypatch):
    monkeypatch.setattr(optimizer, 'T_SCORE', 10.0)
    report = str(opt)
    assert 'ОПТИМИЗАЦИЯ НЕ ТРЕБУЕТСЯ' in report
    t_score = 2.17621763863156
    assert f'Прирост просадки составляет {t_score:.2f} СКО < 10.00' in report


def test_str_t_score(opt):
    report = str(opt)
    assert 'ОПТИМИЗАЦИЯ ТРЕБУЕТСЯ' in report
    t_score = 2.17621763863156
    assert f'Прирост просадки составляет {t_score:.2f} СКО > 2.00' in report


def test_str_dividends(opt, monkeypatch):
    monkeypatch.setattr(Optimizer, 't_drawdown_growth', 0)
    report = str(opt)
    assert 'ОПТИМИЗАЦИЯ НЕ ТРЕБУЕТСЯ' in report
    t_score = 0.613956329529872
    assert f'Прирост дивидендов составляет {t_score:.2f} СКО < 2.00' in report
