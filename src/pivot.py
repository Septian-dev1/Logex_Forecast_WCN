"""
Pivot Table Engine

Modul untuk mencetak pivot table ke terminal dan membangun
DataFrame pivot untuk ekspor ke file Excel.
"""

import numpy as np
import pandas as pd


def print_text_pivot(df_mentah: pd.DataFrame, df_pro_master: pd.DataFrame, target_year: int, target_spec: str):
    """
    Mencetak pivot table volume (Aktual, SQL, Prophet) secara tekstual ke konsol/terminal.

    Parameters:
        df_mentah (pd.DataFrame): DataFrame berisi data historis mentah.
        df_pro_master (pd.DataFrame): Master DataFrame hasil prediksi Prophet.
        target_year (int): Tahun yang difilter.
        target_spec (str): Kode spesialisasi yang difilter.
    """
    df_yr = df_mentah[
        (df_mentah['year'] == target_year) &
        (df_mentah['specialism_code'] == target_spec)
    ].copy()
    
    if df_yr.empty:
        return
        
    df_yr.drop_duplicates(inplace=True)
    df_yr.dropna(subset=['year', 'month', 'volume'], inplace=True)
    
    if df_yr['volume'].dtype in ['object', 'O']:
        df_yr['volume'] = df_yr['volume'].astype(str).str.replace(',', '.').astype(float)
        
    sql_grp = (df_yr.groupby(['monitor_month', 'is_forecast', 'month'])['volume']
               .sum().unstack('month'))
    if not sql_grp.empty:
        sql_grp.columns = [int(c) for c in sql_grp.columns]

    pro_grp = pd.DataFrame()
    if not df_pro_master.empty:
        pro_yr = df_pro_master[
            (df_pro_master['year'] == target_year) &
            (df_pro_master['specialism_code'] == target_spec)
        ]
        if not pro_yr.empty:
            pro_grp = pro_yr.groupby(['monitor_month', 'month'])['yhat'].sum().unstack('month')
            pro_grp.columns = [int(c) for c in pro_grp.columns]

    monitors_in_year = sorted(df_yr['monitor_month'].unique())
    q_monitors_yr = [m for m in monitors_in_year if int(m.split('-')[1]) in [1, 4, 7, 10]]
    months = list(range(1, 13))
    sep = "-" * 140
    col_hdr = f"{'Monitor / Tipe':<30}" + "".join(f"{str(m):>9}" for m in months) + f"{'Grand Total':>13}"

    def fmt_num(v, width):
        s = f"{round(v):,}".replace(",", ".")
        return s.rjust(width)

    def fmt_row(label, data, months):
        vals = []
        for m in months:
            v = data.get(m, np.nan)
            vals.append(fmt_num(v, 9) if pd.notna(v) else "         ")
        total = sum(data.get(m, 0) for m in months if pd.notna(data.get(m, np.nan)))
        return f"{label:<30}" + "".join(vals) + fmt_num(total, 13)

    print("\n" + "=" * 140)
    print(f"  PIVOT TABLE — Spesialisasi: {target_spec}  |  Filter: Tahun = {target_year}")
    print("=" * 140)
    print(col_hdr)
    print(sep)

    for mon in q_monitors_yr:
        row_0 = sql_grp.loc[(mon, 0)].to_dict() if (mon, 0) in sql_grp.index else {}
        row_1 = sql_grp.loc[(mon, 1)].to_dict() if (mon, 1) in sql_grp.index else {}
        row_p = pro_grp.loc[mon].to_dict() if mon in pro_grp.index else {}

        if pd.notna(row_0.get(12, np.nan)):
            row_1 = {}
            row_p = {}

        if row_1:
            row_p = {m: v for m, v in row_p.items() if pd.notna(row_1.get(m, np.nan))}
        else:
            row_p = {}

        mon_data = {}
        for m in months:
            if pd.notna(row_0.get(m, np.nan)): mon_data[m] = row_0[m]
            elif pd.notna(row_1.get(m, np.nan)): mon_data[m] = row_1[m]

        print(fmt_row(f"■ {mon}", mon_data, months))
        if row_0: print(fmt_row("    0  Aktual", row_0, months))
        if row_1: print(fmt_row("    1  Forecast SQL", row_1, months))
        if row_p: print(fmt_row("    P  Forecast Prophet", row_p, months))
        print(sep)

    gt_all = {}
    for m in months:
        gt_all[m] = sql_grp[m].sum() if m in sql_grp.columns else np.nan
    print(fmt_row("GRAND TOTAL", gt_all, months))
    print("=" * 140)


def build_pivot_dataframe(df_mentah: pd.DataFrame, df_pro_master: pd.DataFrame, target_year: int, target_spec: str) -> pd.DataFrame:
    """
    Membangun struktur DataFrame Pivot untuk keperluan ekspor ke file Excel.

    Parameters:
        df_mentah (pd.DataFrame): DataFrame historis mentah.
        df_pro_master (pd.DataFrame): Master DataFrame Prophet forecast.
        target_year (int): Tahun yang difilter.
        target_spec (str): Spesialisasi yang diproses.

    Returns:
        pd.DataFrame: DataFrame yang memuat representasi tabel pivot per bulan (Jan - Des).
    """
    df_yr = df_mentah[
        (df_mentah['year'] == target_year) &
        (df_mentah['specialism_code'] == target_spec)
    ].copy()
    
    if df_yr.empty: return pd.DataFrame()

    df_yr.drop_duplicates(inplace=True)
    df_yr.dropna(subset=['year', 'month', 'volume'], inplace=True)
    
    if df_yr['volume'].dtype in ['object', 'O']:
        df_yr['volume'] = df_yr['volume'].astype(str).str.replace(',', '.').astype(float)

    sql_grp = (df_yr.groupby(['monitor_month', 'is_forecast', 'month'])['volume']
               .sum().unstack('month'))
    if not sql_grp.empty: sql_grp.columns = [int(c) for c in sql_grp.columns]

    pro_grp = pd.DataFrame()
    if not df_pro_master.empty:
        pro_yr = df_pro_master[
            (df_pro_master['year'] == target_year) &
            (df_pro_master['specialism_code'] == target_spec)
        ]
        if not pro_yr.empty:
            pro_grp = pro_yr.groupby(['monitor_month', 'month'])['yhat'].sum().unstack('month')
            pro_grp.columns = [int(c) for c in pro_grp.columns]

    monitors_in_year = sorted(df_yr['monitor_month'].unique())
    q_monitors_yr = [m for m in monitors_in_year if int(m.split('-')[1]) in [1, 4, 7, 10]]
    months = list(range(1, 13))
    pivot_rows = []

    for mon in q_monitors_yr:
        row_0 = sql_grp.loc[(mon, 0)].to_dict() if (mon, 0) in sql_grp.index else {}
        row_1 = sql_grp.loc[(mon, 1)].to_dict() if (mon, 1) in sql_grp.index else {}
        row_p = pro_grp.loc[mon].to_dict() if mon in pro_grp.index else {}

        if pd.notna(row_0.get(12, np.nan)):
            row_1 = {}; row_p = {}

        if row_1: row_p = {m: v for m, v in row_p.items() if pd.notna(row_1.get(m, np.nan))}
        else: row_p = {}

        mon_data = {}
        for m in months:
            if pd.notna(row_0.get(m, np.nan)): mon_data[m] = row_0[m]
            elif pd.notna(row_1.get(m, np.nan)): mon_data[m] = row_1[m]

        def make_row(label, data):
            r = {'Spesialisasi': target_spec, 'Monitor_Month': mon, 'Tipe': label}
            grand = 0
            for m in months:
                v = data.get(m, np.nan)
                r[str(m)] = round(v) if pd.notna(v) else np.nan
                if pd.notna(v): grand += v
            r['Grand Total'] = round(grand)
            return r

        pivot_rows.append(make_row(f'■ {mon}', mon_data))
        if row_0: pivot_rows.append(make_row('  0  Aktual', row_0))
        if row_1: pivot_rows.append(make_row('  1  Forecast SQL', row_1))
        if row_p: pivot_rows.append(make_row('  P  Forecast Prophet', row_p))

    if not pivot_rows: return pd.DataFrame()
    
    gt_data = {}
    for m in months:
        gt_data[m] = sql_grp[m].sum() if m in sql_grp.columns else np.nan
    pivot_rows.append(make_row('GRAND TOTAL', gt_data))
    
    return pd.DataFrame(pivot_rows)
