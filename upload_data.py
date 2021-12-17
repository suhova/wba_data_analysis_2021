import pandas as pd
import numpy as np

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from clickhouse_driver import Client
import pandas as pd
import os
import glob

config = pd.read_csv('config.csv')
ch_host = config[config.conf == 'ch_host'].value.values[0]
ch_port = config[config.conf == 'ch_port'].value.values[0]
client = Client(host=ch_host, user='default', password='', port=ch_port, database='wba')

path = "./data/"
csv_files = glob.glob(os.path.join(path, "*.csv"))
for f in csv_files:
    file = pd.read_csv(f)
    file = file.replace('..', np.nan)
    file = file.rename(
        columns={'Country Name': 'country_name', 'Country Code': 'country_code', 'Series Name': 'indicator_name',
                 'Series Code': 'indicator_code', 'year': 'time'})
    file = file.replace('..', np.nan).dropna()
    file.columns.values[4] = file.columns.values[4].split(' ')[0]
    years = file.columns.values[4:]
    file = pd.melt(file, id_vars=file.columns.values[:4], value_vars=years, var_name='year')
    file = file.reset_index(drop=True)
    file["value"] = file.value.astype(float)
    file["year"] = file.year.astype(int)
    tuples = [tuple(x) for x in file.values]
    client.execute('INSERT INTO economic_data VALUES', tuples)

client.execute("OPTIMIZE TABLE economic_data")
print(client.execute("SELECT count(*) from economic_data"))
