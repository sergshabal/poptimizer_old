# Оптимизация долгосрочного портфеля акций

[![Build Status](https://travis-ci.org/WLM1ke/PortfolioOptimizer.svg?branch=master)](https://travis-ci.org/WLM1ke/PortfolioOptimizer) [![codecov](https://codecov.io/gh/WLM1ke/PortfolioOptimizer/branch/master/graph/badge.svg)](https://codecov.io/gh/WLM1ke/PortfolioOptimizer)


## Цель:
Воспроизвести на базе Python существующую модель управления долгосрочным инвестиционным портфелем российских акций на базе Excel и усовершенствовать ее с помощью автоматизации загрузки данных и методов машинного обучения

## Этапы работы:
1. Загрузчики необходимых данных
- [x] Информация по размерам лотов и последней цене
- [x]  История котировок акций
- [x] Индекс полной доходности MOEX
- [x] CPI
- [х] Дивиденды

2. Трансформация данных
- [ ] Организация хранения локальной версии данных
- [ ] Пересчет в реальные показатели
- [ ] Перевод в месячные таймфреймы

3. Ключевы метрики портфеля
- [ ] Простой DGP для волатильности и доходности портфеля
- [ ] Метрики дивидендного потока
- [ ] Метрики стоимости потортфеля

4. Оптимизационная процедура
- [ ] Доминирование по Парето
- [ ] Выбор оптимального направления
  
5. Усовершенстование существующей модели
- [ ] Скользящий месячный таймфрейм
- [ ] Скользящий таймфрейм по дивидендам
- [ ] Применение ML
