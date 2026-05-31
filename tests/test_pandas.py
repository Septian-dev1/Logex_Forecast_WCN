import pandas as pd

fc_q = pd.DataFrame({
    'specialism_code': ['A', 'A', 'B'],
    'ds': ['2023-01-01', '2023-01-01', '2023-01-01'],
    'monitor_month_dt': pd.to_datetime(['2022-12-01', '2022-11-01', '2022-12-01']),
    'yhat': [10, 20, 30]
})
fc_q['ds'] = pd.to_datetime(fc_q['ds'])

def pick_best(group):
    ds_val = group.name[1]
    valid = group[group['monitor_month_dt'] <= ds_val]
    if valid.empty: valid = group
    res = group.loc[[valid['monitor_month_dt'].idxmax()]].copy()
    res['specialism_code'] = group.name[0]
    res['ds'] = group.name[1]
    return res

fc_best = fc_q.groupby(['specialism_code', 'ds'], group_keys=False).apply(pick_best).reset_index(drop=True).rename(columns={'yhat': 'vol_spec_total'})
print(fc_best.columns)
print(fc_best)
