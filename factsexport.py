import pandas as pd
import requests

# importuje metryki, ich opisy, zakres dat i ostatnia wartosc dla danego cik

headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
cik = '0001652044'  # googl

facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
factsl = []
for label in facts['facts']['us-gaap'].keys():
    description = facts['facts']['us-gaap'][label]['description']
    unit =list(facts['facts']['us-gaap'][label]['units'].keys())[0]
    period_objs = facts['facts']['us-gaap'][label]['units'][unit]
    ends = []
    for period_obj in period_objs:
        end = period_obj['end']
        ends.append(end)
    min_end = min(ends)
    max_end = max(ends)
    last_val = None
    for period_obj in period_objs:
        end = period_obj['end']
        if end == max_end:
            last_val = period_obj['val'] / 1000000

    factsl.append([label, description, unit, min_end, max_end, last_val])

df = pd.DataFrame(factsl)
df.columns = ['label', 'description', 'unit', 'min_end', 'max_end', 'last_val']
df.to_excel('C:\\Users\\barto\Desktop\\SEC2024\\facts_desc.xlsx')
