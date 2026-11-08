# Лабораторная работа № 3 — Wine Quality / CRISP-DM

**ДГТУ · МИК21**  
Дисциплина: «Проект — применение машинного обучения в креативных индустриях».

[Открыть notebook на GitHub](Lab3_CRISPDM_Wine_Quality_MIK21.ipynb) · [Запустить в Google Colab](https://colab.research.google.com/github/localzet/localzet/blob/main/education/dgtu/ml-creative-industries/lab03-wine-quality/Lab3_CRISPDM_Wine_Quality_MIK21.ipynb)

## Содержание

Все шесть этапов CRISP-DM: постановка задачи, паспорт и EDA данных, очистка и безопасное разбиение, сравнение baseline/Ridge/RandomForest/HistGradientBoosting, независимая оценка MAE/RMSE/R², анализ ошибок и демонстрационное предсказание.

**Запуск:** открыть в Google Colab, выбрать «Среда выполнения → Выполнить все». Нужны pandas, numpy, matplotlib, scikit-learn, joblib (обычно доступны в Colab). Датасет загружается автоматически из публичного зеркала Kaggle CSV с проверкой Git blob SHA-1. Если ссылка недоступна, вручную скачать `winequalityN.csv` из Kaggle и положить рядом с notebook.

Исходный CSV: 6497 строк, 13 колонок, 38 пропусков, 1168 полностью повторяющихся строк. Точные повторы исключаются, а объекты с одинаковыми входными характеристиками не пересекают train/validation/test. Метрики обучения вычисляются во время выполнения: их значения не следует указывать как результаты до запуска.

### Данные и атрибуция

- [Wine Quality, Kaggle (rajyellow46)](https://www.kaggle.com/datasets/rajyellow46/wine-quality)
- [UCI Machine Learning Repository: Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality)
- Cortez et al. (2009), *Modeling wine preferences by data mining from physicochemical properties*, Decision Support Systems. Данные UCI: CC BY 4.0.

Прототип предназначен для учебной демонстрации и не заменяет экспертную дегустацию.
