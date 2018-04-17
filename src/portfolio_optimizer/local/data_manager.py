"""Организация создания, обновления и предоставления локальных данных"""

import arrow
import numpy as np
import pandas as pd

from portfolio_optimizer.local.data_file import DataFile

MARKET_TIME_ZONE = 'Europe/Moscow'
# Торги заканчиваются в 19.00, но данные публикуются 19.45
END_OF_CURRENT_TRADING_DAY = arrow.now(MARKET_TIME_ZONE).replace(hour=19, minute=45, second=0, microsecond=0)


class DataManager:
    """Организация создания, обновления и предоставления локальных данных"""

    def __init__(self, frame_category: str, frame_name: str, source_function, update_function=None):
        """
        Parameters
        ----------
        frame_category
            Каталог в директории данных, где хранится информация
        frame_name
            Название файла, где хранится информация
        source_function
            Функция загрузки данных из web - не принимает параметры и используется для создания локальных данных
        update_function
            Функция загрузки данных из web - принимает один аргумент start последний элемент индекса локальных данных и
            используется для обновления существующих данных. Если None, то при обновлении будут загружены все данные с
            помощью функции source_function
        """
        self.frame_category = frame_category
        self.frame_name = frame_name
        self.source_function = source_function
        self.update_function = update_function
        self.file = DataFile(frame_category, frame_name)
        if self.file.last_update():
            self.update()
        else:
            self.create()

    def update(self):
        """Обновляет локальные данные, если наступило время очередного обновления

        Во время обновления проверяется совпадение новых данных со существующими
        """
        if self._need_update():
            df_old = self.get()
            if self.update_function:
                df_new = self.update_function(start=df_old.index[-1])
            else:
                df_new = self.source_function()
            self._validate(df_old, df_new)
            new_elements = df_new.index.difference(df_old.index)
            full_index = df_old.index.append(new_elements)
            df_full = df_old.reindex(index=full_index)
            df_full.loc[new_elements] = df_new.loc[new_elements]
            self.file.dump(df_full)

    def _need_update(self):
        """Файлы обновляются раз в день после публикации информации по котировкам"""
        if arrow.now() > END_OF_CURRENT_TRADING_DAY:
            end_of_last_trading_day = END_OF_CURRENT_TRADING_DAY
        else:
            end_of_last_trading_day = END_OF_CURRENT_TRADING_DAY.shift(days=-1)
        if self.file.last_update() < end_of_last_trading_day:
            return True
        return False

    def _validate(self, df_old, df_new):
        """Проверяет соответствие новых данных существующим"""
        if not df_new.index.is_unique:
            raise ValueError(f'У новых данных не уникальный индекс {df.new}')
        common_index = df_old.index.intersection(df_new.index)
        if isinstance(df_old, pd.Series):
            condition = np.allclose(df_old.loc[common_index], df_new.loc[common_index])
        else:
            condition_not_object = np.allclose(df_old.select_dtypes(exclude='object').loc[common_index],
                                               df_new.select_dtypes(exclude='object').loc[common_index])
            df_new_object = df_new.select_dtypes(include='object').loc[common_index]
            condition_object = df_old.select_dtypes(include='object').loc[common_index].equals(df_new_object)
            condition = condition_not_object and condition_object
        message = (f'Ошибка обновления данных - существующие данные не соответствуют новым:\n'
                   f'Категория - {self.frame_category}\n'
                   f'Название - {self.frame_name}\n')
        if not condition:
            raise ValueError(f'{message}{df_old}{df_new}')

    def create(self):
        """Создает локальный файл с нуля или перезаписывает существующий"""
        df = self.source_function()
        if not df.index.is_unique:
            raise ValueError(f'У новых данных не уникальный индекс {df}')
        self.file.dump(df)

    def get(self):
        """Получение данных"""
        return self.file.load()