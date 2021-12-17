Предсказание ВВП на основе данных о темпах роста ВВП, безработицы и инфляции с сайта WBA.

wba_data_analysis_2021/superset/install.sh для развёртывания Superset и Clickhouse
wba_data_analysis_2021/upload_data.py - скрипт для загрузки входных данных, сложенных в data (по аналогии с 1960.csv)
wba_data_analysis_2021/var_unemployment.py - расчёт предсказания ВВП и запись результата в CH. Для предсказания необходимо загрузить данные минимум за 15 лет. 

Для доступа к песочнице с загруженными данными перейти в Superset https://localhost:8088 (admin, admin)
