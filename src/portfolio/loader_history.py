"""Quotes history downloader and parser for tickers and MOEX Russia Net Total Return (Resident) Index."""

import datetime

import pandas as pd
import requests


def get_json(url: str):
    """Return json found at *url*."""
    response = requests.get(url)
    return response.json()


def make_url(base: str, ticker: str, start_date=None, block_position=0):
    """Create url based on components.
    
    Parameters
    ----------
    base
        Основная часть url.
    ticker
        Наименование тикера.
    start_date : date.time or None
        Начальная дата котировок. Если предоставлено значение None 
        - данные запрашиваются с начала имеющейся на сервере ISS 
        истории котировок.
    block_position : int
        Позиция курсора, начиная с которой необходимо получить очередной блок 
        данных. При большом запросе сервер ISS возвращает данные блоками обычно 
        по 100 значений. Нумерация позиций в ответе идет с 0.

    Returns
    -------
    str
        Строка url для запроса.        
    """
    if not base.endswith('/'):
        base += '/'
    url = base + f'{ticker}.json'
    query_args = [f'start={block_position}']
    if start_date:
        if not isinstance(start_date, datetime.date):
            raise TypeError(start_date)
        query_args.append(f"from={start_date:%Y-%m-%d}")
    arg_str = '&'.join(query_args)
    return f'{url}?{arg_str}'
    

class TotalReturn:
    """
    Представление ответа сервера - данные по индексу полной доходности MOEX.
      
       В ответе сервера:
         - по ключу history - словарь с историей котировок
         - во вложеном словаре есть ключи columns и data 
           с масивами описания колонок и данными           
    """
    base = 'http://iss.moex.com/iss/history/engines/stock/markets/index/boards/RTSI/securities'
    ticker = 'MCFTRR'

    def __init__(self, start_date, block_position):
        self.url = make_url(self.base, self.ticker,
                            start_date=start_date,
                            block_position=block_position)
        self.data = get_json(self.url)
        self.validate(block_position) 

    def validate(self, block_position):
        if len(self) == 0 and block_position == 0:
            raise ValueError('Пустой ответ. '
                             f'Возможно ошибка в запросе: {self.url}')
        
    def __len__(self):
        return len(self.values)

    def __bool__(self):
        return self.__len__() > 0

    @property
    def values(self):
        return self.data['history']['data']

    @property
    def columns(self):
        return self.data['history']['columns']       
    
    @property
    def dataframe(self):
        df = pd.DataFrame(data=self.values, columns=self.columns)
        return df[['TRADEDATE', 'CLOSE']].set_index('TRADEDATE')


class Ticker(TotalReturn):
    """
    Представление ответа сервера по отдельному тикеру.
    """
    base = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities'

    def __init__(self, ticker, start_date, block_position):
        self.ticker = ticker
        self.url = make_url(self.base, ticker, start_date, block_position)
        self.data = get_json(self.url)
        self.validate(block_position)

    @property
    def dataframe(self):
        df = pd.DataFrame(data=self.values, columns=self.columns)
        # Часто объемы не распознаются, как численные значения
        df['VOLUME'] = pd.to_numeric(df['VOLUME'])
        return df[['TRADEDATE', 'CLOSE', 'VOLUME']]


def yield_data_blocks(start_date, cls_maker):
    """Yield pandas DataFrames until response length is exhausted."""
    block_position = 0
    current_response = True
    while current_response:
        current_response = cls_maker(start_date, block_position)
        block_position += len(current_response)
        yield current_response.dataframe


def get_index_history(start_date):
    """
    Возвращает историю котировок индекса полной доходности с учетом российских налогов.

    Parameters
    ----------
    start_date : datetime.date or None
        Начальная дата котировок. 
        
    Returns
    -------
    pandas.DataFrame
        В строках даты торгов.
        В столбцах цена закрытия индекса полной доходности.
    """
    gen = yield_data_blocks(start_date, TotalReturn)
    return pd.concat(gen)


def get_index_history_from_start():
    """
    Возвращает историю котировок индекса полной доходности с учетом 
    российских налогов с начала информации.
    Данные запрашиваются с начала имеющейся на сервере ISS истории котировок.
    Предполагаемая дата начала котировок - 2003-02-26.    
    """
    return get_index_history(start_date=None)


def get_ticker_history(ticker, start_date):
    """
    Возвращает историю котировок тикера.

    Parameters
    ----------
    ticker : str
        Тикер, например, 'MOEX'.

    start_date : datetime.date or None
        Начальная дата котировок.

    Returns
    -------
    pandas.DataFrame
        В строках даты торгов.
        В столбцах цена закрытия и оборот в штуках.
    """

    # builder function to return Ticket instances - a workaround
    def ticker_maker(date, offset):
        return Ticker(ticker, date, offset)

    gen = yield_data_blocks(start_date, ticker_maker)
    df = pd.concat(gen, ignore_index=True)
    # Для каждой даты выбирается режим торгов с максимальным оборотом
    df = df.loc[df.groupby('TRADEDATE')['VOLUME'].idxmax()]
    return df.set_index('TRADEDATE')


def get_ticker_history_from_start(ticker):
    """
    Возвращает историю котировок тикера с начала информации.
    Данные запрашиваются с начала имеющейся на сервере ISS истории котировок.
    Начальная дата различается для разных тикеров.
    """
    return get_ticker_history(ticker, start_date=None)


if __name__ == '__main__':
    z = get_ticker_history('MOEX', datetime.date(2017, 10, 2))
    print(z)