"""Загружает данные по предстоящим дивидендам с https://www.smart-lab.ru"""

import pandas as pd
from bs4 import BeautifulSoup

from web.labels import TICKER, DATE, DIVIDENDS
from web.web_dividends_dohod import get_html_table

URL = 'https://smart-lab.ru/dividends/index/order_by_short_name/desc/'
# Номер таблицы с дивидендами в документе
TABLE_INDEX = 2
# Позиции и наименования ключевых столбцов
TH_TICKER = 'Тикер'
TH_DATE = 'дата отсечки'
TH_VALUE = 'дивиденд,руб'
TICKER_COLUMN = 1
DATE_COLUMN = 4
VALUE_COLUMN = 7


class RowParser:
    """Выбирает столбцы в ряду с тикером, датой закрытия реестра и дивидендами"""

    def __init__(self, row: BeautifulSoup, is_header: bool = False):
        if is_header:
            column_html_tag = 'th'
        else:
            column_html_tag = 'td'
        self.columns = [column.text for column in row.find_all(column_html_tag)]

    @property
    def ticker(self):
        """Тикер"""
        return self.columns[TICKER_COLUMN]

    @property
    def date(self):
        """Дата закрытия реестра"""
        return self.columns[DATE_COLUMN]

    @property
    def value(self):
        """Размер дивиденда"""
        return self.columns[VALUE_COLUMN]


def validate_table_header(header: BeautifulSoup):
    """Проверка количества столбцов и наименований с датой закрытия и дивидендами"""
    columns_count = len(header.find_all('th'))
    if columns_count != 10:
        raise ValueError('Некорректные заголовки таблицы дивидендов.')
    cells = RowParser(header, True)
    if cells.ticker != TH_TICKER or cells.date != TH_DATE or cells.value != TH_VALUE:
        raise ValueError('Некорректные заголовки таблицы дивидендов.')


def validate_table_footer(footer: BeautifulSoup):
    """В последнем ряду должна быть одна ячейка"""
    columns_count = len(footer.find_all('td'))
    if columns_count != 1:
        raise ValueError('Некорректная последняя строка таблицы дивидендов.')


def parse_table_rows(table: BeautifulSoup):
    """Строки с прогнозом имеют class = dividend_approved"""
    rows = table.find_all(name='tr')
    validate_table_header(rows[0])
    validate_table_footer(rows[-1])
    for row in rows[1:-1]:
        if 'dividend_approved' in row['class']:
            cells = RowParser(row)
            yield (cells.ticker,
                   pd.to_datetime(cells.date, dayfirst=True),
                   pd.to_numeric(cells.value.replace(',', '.')))
        else:
            # Если появятся, то надо разобраться, как их корректно обрабатывать
            raise ValueError('Не утвержденные дивиденды')


def make_df(parsed_rows):
    """Формирует DataFrame"""
    df = pd.DataFrame(data=parsed_rows,
                      columns=[TICKER, DATE, DIVIDENDS])
    return df.set_index(TICKER)


def dividends_smart_lab():
    """
    Возвращает ожидаемые дивиденды с сайта https://smart-lab.ru/

    Returns
    -------
    pandas.DataFrame
        Строки - тикеры
        столбцы - даты закрытия и дивиденды
    """
    table = get_html_table(URL, TABLE_INDEX)
    parsed_rows = parse_table_rows(table)
    return make_df(parsed_rows)


if __name__ == '__main__':
    print(dividends_smart_lab())
