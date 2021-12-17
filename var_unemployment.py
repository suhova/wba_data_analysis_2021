import pandas as pd
from statsmodels.tsa.vector_ar.var_model import VAR
from clickhouse_driver import Client

def var(data, step_count):
    model = VAR(data.to_numpy().tolist())
    results = model.fit()
    return results.forecast(results.endog, steps=step_count)[:, 0]

config = pd.read_csv('config.csv')
ch_host = config[config.conf == 'ch_host'].value.values[0]
ch_port = config[config.conf == 'ch_port'].value.values[0]
client = Client(host=ch_host, user='default', password='', port=ch_port, database='wba')

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ep = pd.DataFrame(client.execute("SELECT country_name, time, value FROM economic_data "
                    "where indicator_name = 'GDP growth (annual %)'"),
                   columns = ['country_name', 'time', 'gdp_growth_annual'])
fs1 = pd.DataFrame(client.execute("SELECT country_name, time, value FROM economic_data "
                    "where indicator_name = 'Inflation, consumer prices (annual %)'"),
                   columns = ['country_name', 'time', 'inflation_consumer_prices_annual'])
fs2 = pd.DataFrame(client.execute("SELECT country_name, time, value FROM economic_data "
                    "where indicator_name = 'Deposit interest rate (%)'"),
                   columns = ['country_name', 'time', 'deposit_interest_rate'])
fs = fs1.merge(fs2, left_on=["country_name", "time"], right_on=["country_name", "time"])

sp = pd.DataFrame(client.execute("SELECT country_name, time, value FROM economic_data "
                    "where indicator_name = 'Unemployment, total (% of total labor force) (modeled ILO estimate)'"),
                   columns = ['country_name', 'time', 'unemployment_total__of_total_labor_force__modeled_ilo_estimate'])
fs["inflation_growth_rate"] = fs["inflation_consumer_prices_annual"].diff()
fs = fs.drop("inflation_consumer_prices_annual", axis=1)
sp["unemployment_growth_rate"] = sp["unemployment_total__of_total_labor_force__modeled_ilo_estimate"].diff()
sp = sp.drop("unemployment_total__of_total_labor_force__modeled_ilo_estimate", axis=1)
combined = ep.merge(fs, left_on=["country_name", "time"], right_on=["country_name", "time"])
combined = combined.merge(sp, left_on=["country_name", "time"], right_on=["country_name", "time"])
combined = combined.dropna()
combined["time"] = combined.time.astype(int)
max_year = combined['time'].max()
year = max_year - 10
countries = combined['country_name'].drop_duplicates().sort_values().to_numpy()

for x in range(0, 15):
    s = f"time < {year}"
    new_data_list = []
    for c in countries:
        part = combined.loc[combined['country_name'] == c]
        part = part.query(s)
        if len(part) < 15:  # not enough data
            continue
        try:
            step_n = 1
            if year == max_year :
                step_n = 5
            res = var(part[["gdp_growth_annual", "inflation_growth_rate", "unemployment_growth_rate"]], step_n)
        except Exception as e:
            repr(e)
            continue

        last_year = year
        years = range(last_year+1, last_year + 1 + step_n)
        for time, gdp in zip(years, res):
            new_data_list.append((c, time, gdp))
    SQL_query = 'INSERT INTO economic_policy_prediction VALUES'
    client.execute(SQL_query, new_data_list)
    year += 1

SQL_optimize = "OPTIMIZE TABLE economic_policy_prediction"
client.execute(SQL_optimize)
print(client.execute("SELECT COUNT(*) FROM economic_policy_prediction"))