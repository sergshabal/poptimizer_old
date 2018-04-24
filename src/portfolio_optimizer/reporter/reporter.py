"""Хранение истории стоимости портфеля и составление отчетов"""

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame

from portfolio_optimizer import Portfolio
from portfolio_optimizer.reporter import value_dynamics
from portfolio_optimizer.reporter import value_structure
from portfolio_optimizer.settings import REPORTS_PATH

# Наименование файла отчета
REPORT_NAME = str(REPORTS_PATH / 'report.pdf')

# Каталог с данными
REPORTS_DATA_PATH = REPORTS_PATH / 'data'

# Лис с данными
SHEET_NAME = 'Data'


def read_data(report_name: str):
    data = pd.read_excel(REPORTS_DATA_PATH / f'{report_name}.xlsx',
                         sheet_name=SHEET_NAME,
                         header=0,
                         index_col=0,
                         converters={'Date': pd.to_datetime})
    return data


def make_report(report_name: str, portfolio: Portfolio, years: int = 5):
    """Формирует отчет"""
    page_width, page_height = A4
    margin = cm
    blank_width = (page_width - 2 * margin) / 3
    blank_height = (page_height - 2 * margin) / 3

    frame_l1 = Frame(margin, margin + blank_height * 2,
                     blank_width, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)
    frame_l2 = Frame(margin, margin + blank_height,
                     blank_width, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)
    frame_l3 = Frame(margin, margin,
                     blank_width, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)
    frame_r1 = Frame(margin + blank_width, margin + blank_height * 2,
                     blank_width * 2, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)
    frame_r2 = Frame(margin + blank_width, margin + blank_height,
                     blank_width * 2, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)
    frame_r3 = Frame(margin + blank_width, margin,
                     blank_width * 2, blank_height,
                     leftPadding=0, bottomPadding=0,
                     rightPadding=0, topPadding=6,
                     showBoundary=0)

    canvas = Canvas(REPORT_NAME, pagesize=(page_width, page_height))

    canvas.setFont('Helvetica-Bold', size=14)
    canvas.setFillColor(colors.darkblue)
    canvas.drawString(margin, margin * 1.1 + 3 * blank_height, f'PORTFOLIO REPORT: {portfolio.date}')
    canvas.setStrokeColor(colors.darkblue)
    canvas.line(margin, margin + 3 * blank_height, margin + blank_width * 3, margin + 3 * blank_height)
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.line(margin, margin + 2 * blank_height, margin + blank_width * 3, margin + 2 * blank_height)
    canvas.line(margin, margin + blank_height, margin + blank_width * 3, margin + blank_height)

    data = read_data('report')
    image1 = value_dynamics.make_plot(data[-61:], blank_width / inch * 2, blank_height / inch * 0.95)
    image1.drawOn(canvas, margin + blank_width, margin + blank_height * 2.025)

    table1 = value_dynamics.make_dynamics_table(data[-61:])

    image2 = value_structure.make_plot(portfolio, blank_width / inch * 2 * 0.95, blank_height / inch * 0.95)
    image2.drawOn(canvas, margin + blank_width, margin + blank_height * 1.025)

    table2 = value_structure.make_table(portfolio)

    table3 = value_dynamics.make_flow_table(data[-61:])

    frame_l1.addFromList([table1], canvas)
    frame_l2.addFromList([table2], canvas)
    frame_l3.addFromList([], canvas)
    frame_r1.addFromList([], canvas)
    frame_r2.addFromList([], canvas)
    frame_r3.addFromList([table3], canvas)

    canvas.save()


# TODO: сделать прокладывание пути
# TODO: поправить кривой круг


if __name__ == '__main__':
    POSITIONS = dict(BANEP=200,
                     MFON=55,
                     SNGSP=235,
                     RTKM=0,
                     MAGN=0,
                     MSTT=4435,
                     KBTK=9,
                     MOEX=0,
                     RTKMP=1475 + 312 + 91,
                     NMTP=0,
                     TTLK=0,
                     LSRG=561 + 0 + 80,
                     LSNGP=81,
                     PRTK=70,
                     MTSS=749,
                     AKRN=795,
                     MRKC=0,
                     GAZP=0,
                     AFLT=0,
                     MSRS=699,
                     UPRO=1267,
                     PMSBP=1188 + 322 + 219,
                     CHMF=0,
                     GMKN=166 + 28,
                     VSMO=73,
                     RSTIP=87,
                     PHOR=0,
                     MRSB=0,
                     LKOH=123,
                     ENRU=319 + 148,
                     MVID=264 + 62)
    CASH = 596_156 + 470_259 + 54_615
    DATE = '2018-04-19'
    port = Portfolio(date=DATE,
                     cash=CASH,
                     positions=POSITIONS)
    make_report('qqq', port)