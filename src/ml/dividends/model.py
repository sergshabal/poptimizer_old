"""ML-модель для предсказания дивидендов"""
import pandas as pd

from ml import hyper
from ml.dividends import cases
from ml.model_base import BaseModel
from utils.aggregation import Freq

PARAMS = {'data': {'freq': Freq.yearly,
                   'lags': 1},
          'model': {'bagging_temperature': 1.1542008340618164,
                    'depth': 4,
                    'l2_leaf_reg': 2.7558209934423616,
                    'learning_rate': 0.02991973118954086,
                    'one_hot_max_size': 100,
                    'random_strength': 1.024116898045557}}

# Диапазон лагов относительно базового, для которого осуществляется поиск оптимальной ML-модели
LAGS_RANGE = 1


def lags(base_params: dict):
    """Список лагов для оптимизации - должны быть больше 0"""
    base_lags = base_params['data']['lags']
    return [lag for lag in range(base_lags - LAGS_RANGE, base_lags + LAGS_RANGE + 1) if lag > 0]


class DividendsModel(BaseModel):
    """Содержит прогноз дивидендов и его СКО"""
    _PARAMS = PARAMS

    @staticmethod
    def _learn_pool_func(*args, **kwargs):
        """catboost.Pool с данными для обучения"""
        return cases.learn_pool(*args, **kwargs)

    @staticmethod
    def _predict_pool_func(*args, **kwargs):
        """catboost.Pool с данными для предсказания"""
        return cases.predict_pool(*args, **kwargs)

    def _make_data_space(self):
        """Пространство поиска параметров данных модели"""
        space = {'freq': hyper.make_choice_space('freq', Freq),
                 'lags': hyper.make_choice_space('lags', lags(self._PARAMS))}
        return space

    def _check_data_space_bounds(self, params: dict):
        """Проверка, что параметры лежал не около границы вероятностного пространства"""
        lag = params['data']['lags']
        if lag != 1 and (lag == lags(self._PARAMS)[0] or lag == lags(self._PARAMS)[-1]):
            print(f'\nНеобходимо увеличить LAGS_RANGE до {LAGS_RANGE + 1}')

    @property
    def prediction_mean(self):
        """pd.Series с прогнозом дивидендов"""
        data_pool = self._predict_pool_func(tickers=self.positions, last_date=self.date, **self._cv_result['data'])
        return pd.Series(self._clf.predict(data_pool), list(self.positions))

    @property
    def prediction_std(self):
        """pd.Series с прогнозом дивидендов"""
        return pd.Series(self.std, list(self.positions))


if __name__ == '__main__':
    from trading import POSITIONS, DATE

    pred = DividendsModel(tuple(sorted(POSITIONS)), pd.Timestamp(DATE))
    print(pred)
    pred.find_better_model()

    # СКО - 3.9547%
