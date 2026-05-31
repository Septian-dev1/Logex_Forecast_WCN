"""
Pipeline Data Split & Ekspor Detail

Modul ini menghitung proporsi market share asuransi dan 
menguraikan prediksi Prophet ke level granular.
"""

import numpy as np
import pandas as pd


def compute_insurer_split(df_raw: pd.DataFrame, min_volume: int = 10) -> pd.DataFrame:
    """
    Menghitung proporsi market share asuransi (payer) berdasarkan level hierarki: 
    Product, Specialism, atau Hospital Total.
    """
    insurer_col = None
    for cand in ['uzovi_code', 'payer_code']:
        if cand in df_raw.columns:
            insurer_col = cand
            break
            
    if insurer_col is None:
        print("⚠️  Kolom uzovi_code / payer_code tidak ditemukan.")
        return pd.DataFrame()
        
    df = df_raw.copy()
    if 'is_forecast' in df.columns:
        df = df[df['is_forecast'] == 0]
        
    vol_col = 'volume' if 'volume' in df.columns else 'y'
    if df[vol_col].dtype in ['object', 'O']:
        df[vol_col] = df[vol_col].astype(str).str.replace(',', '.').astype(float)
        
    prod_total_map = df.groupby('product_code')[vol_col].sum().rename('prod_total')
    prod_ins_share = df.groupby(['product_code', insurer_col])[vol_col].sum().reset_index().rename(columns={vol_col: 'ins_vol'})
    prod_ins_share = prod_ins_share.merge(prod_total_map.reset_index(), on='product_code')
    prod_ins_share['market_share'] = prod_ins_share['ins_vol'] / prod_ins_share['prod_total']
    
    spec_total_map = df.groupby('specialism_code')[vol_col].sum().rename('spec_total')
    spec_ins_share = df.groupby(['specialism_code', insurer_col])[vol_col].sum().reset_index().rename(columns={vol_col: 'ins_vol'})
    spec_ins_share = spec_ins_share.merge(spec_total_map.reset_index(), on='specialism_code')
    spec_ins_share['market_share'] = spec_ins_share['ins_vol'] / spec_ins_share['spec_total']
    
    hosp_total = df[vol_col].sum()
    hosp_ins_share = df.groupby(insurer_col)[vol_col].sum().reset_index().rename(columns={vol_col: 'ins_vol'})
    hosp_ins_share['market_share'] = hosp_ins_share['ins_vol'] / hosp_total
    hosp_ins_share['split_level'] = 3
    
    all_combos = df.dropna(subset=['product_code', 'specialism_code'])[['product_code', 'specialism_code']].drop_duplicates()
    result_rows = []
    
    for _, row in all_combos.iterrows():
        prod = row['product_code']
        spec = row['specialism_code']
        prod_total = prod_total_map.get(prod, 0)
        spec_total = spec_total_map.get(spec, 0)
        
        if prod_total >= min_volume:
            lvl_rows = prod_ins_share[prod_ins_share['product_code'] == prod]
            for _, r in lvl_rows.iterrows():
                result_rows.append({'product_code': prod, 'specialism_code': spec, 'uzovi_code': r[insurer_col], 'market_share': r['market_share'], 'split_level': 1})
        elif spec_total >= min_volume:
            lvl_rows = spec_ins_share[spec_ins_share['specialism_code'] == spec]
            for _, r in lvl_rows.iterrows():
                result_rows.append({'product_code': prod, 'specialism_code': spec, 'uzovi_code': r[insurer_col], 'market_share': r['market_share'], 'split_level': 2})
        else:
            for _, r in hosp_ins_share.iterrows():
                result_rows.append({'product_code': prod, 'specialism_code': spec, 'uzovi_code': r[insurer_col], 'market_share': r['market_share'], 'split_level': 3})
                
    split_df = pd.DataFrame(result_rows)
    return split_df


def build_granular_lookup(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Membangun matriks pembobot relasional spesialisasi menuju dimensi rinci."""
    df = df_raw.copy()
    if 'is_forecast' in df.columns:
        df = df[df['is_forecast'] == 0]
        
    vol_col = 'volume' if 'volume' in df.columns else 'y'
    dim_cols = [c for c in ['specialism_code', 'product_code', 'diagnosis_code', 'care_type_code', 'care_type'] if c in df.columns]
    
    if vol_col in df.columns and df[vol_col].dtype in ['object', 'O']:
        df[vol_col] = df[vol_col].astype(str).str.replace(',', '.').astype(float)
        
    grp = df.groupby(dim_cols, dropna=False)[vol_col].sum().reset_index().rename(columns={vol_col: 'combo_vol'})
    spec_total = grp.groupby('specialism_code')['combo_vol'].sum().rename('spec_vol')
    grp = grp.merge(spec_total, on='specialism_code')
    grp['combo_weight'] = grp['combo_vol'] / grp['spec_vol'].replace(0, np.nan)
    grp['combo_weight'] = grp['combo_weight'].fillna(0)
    w_sum = grp.groupby('specialism_code')['combo_weight'].transform('sum')
    grp['combo_weight'] = grp['combo_weight'] / w_sum.replace(0, 1)
    
    return grp


def build_forecast_detail(df_raw: pd.DataFrame, df_prophet_master: pd.DataFrame, split_df: pd.DataFrame, monitor_month: str = None) -> pd.DataFrame:
    """Menguraikan Prediksi Prophet Makro menjadi granularisasi setara dengan format output dari SQL pipeline."""
    if df_prophet_master.empty or split_df.empty or 'uzovi_code' not in split_df.columns:
        return pd.DataFrame()
        
    rev_per_vol = {}
    if 'revenue' in df_raw.columns and 'volume' in df_raw.columns:
        df_act = df_raw.copy()
        if 'is_forecast' in df_act.columns: df_act = df_act[df_act['is_forecast'] == 0]
        if df_act['volume'].dtype in ['object', 'O']: df_act['volume'] = df_act['volume'].astype(str).str.replace(',', '.').astype(float)
        grp_rev = df_act.groupby('specialism_code').apply(lambda x: (x['revenue'].sum() / x['volume'].sum() if x['volume'].sum() > 0 else 0))
        rev_per_vol = grp_rev.to_dict()
        
    granular_df = build_granular_lookup(df_raw)
    all_monitors = sorted(df_prophet_master['monitor_month'].unique())
    q_monitors_avail = [m for m in all_monitors if int(str(m).split('-')[1]) in [1, 4, 7, 10]]
    
    fc_all = df_prophet_master.copy()
    fc_all['ds'] = pd.to_datetime(fc_all['ds'])
    fc_q = fc_all[fc_all['monitor_month'].isin(q_monitors_avail)].copy()
    if fc_q.empty: return pd.DataFrame()
    
    fc_q['monitor_month_dt'] = pd.to_datetime(fc_q['monitor_month'])
    def pick_best(group):
        ds_val = group.name[1]
        valid = group[group['monitor_month_dt'] <= ds_val]
        if valid.empty: valid = group
        res = group.loc[[valid['monitor_month_dt'].idxmax()]].copy()
        res['specialism_code'] = group.name[0]
        res['ds'] = group.name[1]
        return res
        
    fc_best = fc_q.groupby(['specialism_code', 'ds'], group_keys=False).apply(pick_best).reset_index(drop=True).rename(columns={'yhat': 'vol_spec_total'})
    fc_best['vol_spec_total'] = fc_best['vol_spec_total'].clip(lower=0)
    
    merged = fc_best.merge(granular_df, on='specialism_code', how='left')
    merged['vol_combo'] = merged['vol_spec_total'] * merged['combo_weight'].fillna(0)
    
    split_join = split_df[['product_code', 'specialism_code', 'uzovi_code', 'market_share', 'split_level']].copy()
    if 'product_code' in merged.columns:
        expanded = merged.merge(split_join, on=['product_code', 'specialism_code'], how='left')
    else:
        split_spec = split_df.groupby(['specialism_code', 'uzovi_code'])[['market_share', 'split_level']].first().reset_index()
        expanded = merged.merge(split_spec, on='specialism_code', how='left')
        
    if 'uzovi_code' in expanded.columns:
        no_uzovi = expanded['uzovi_code'].isna()
        if no_uzovi.any():
            specs_missing = expanded.loc[no_uzovi, 'specialism_code'].unique()
            spec_fallback = split_df[split_df['specialism_code'].isin(specs_missing)].groupby(['specialism_code', 'uzovi_code']).agg(market_share=('market_share', 'first'), split_level=('split_level', 'first')).reset_index()
            merged_missing = expanded[no_uzovi].drop(columns=['uzovi_code', 'market_share', 'split_level'], errors='ignore').merge(spec_fallback, on='specialism_code', how='left')
            expanded = pd.concat([expanded[~no_uzovi], merged_missing], ignore_index=True)
            
    if expanded.empty or 'uzovi_code' not in expanded.columns: return pd.DataFrame()
    
    expanded['volume'] = (expanded['vol_combo'] * expanded['market_share'].fillna(0)).round(7)
    expanded['revenue'] = (expanded['volume'] * expanded['specialism_code'].map(rev_per_vol).fillna(0)).round(6)
    
    result = {
        'monitor_month': expanded['monitor_month'],
        'year': expanded['year'].astype(int),
        'month': expanded['month'].astype(int),
        'product_code': expanded['product_code'] if 'product_code' in expanded.columns else np.nan,
        'specialism_code': expanded['specialism_code'],
        'diagnosis_code': expanded['diagnosis_code'] if 'diagnosis_code' in expanded.columns else np.nan,
        'care_type_code': expanded['care_type_code'] if 'care_type_code' in expanded.columns else (expanded['care_type'] if 'care_type' in expanded.columns else np.nan),
        'payer_code': expanded['uzovi_code'],
        'split_level': expanded['split_level'] if 'split_level' in expanded.columns else np.nan,
        'is_forecast': 1,
        'volume': expanded['volume'],
        'revenue': expanded['revenue']
    }
    
    df_out = pd.DataFrame(result)
    df_out = df_out[df_out['volume'] > 0].copy()
    return df_out.sort_values(['monitor_month', 'specialism_code', 'year', 'month']).reset_index(drop=True)
