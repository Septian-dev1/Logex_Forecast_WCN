import pandas as pd

df = pd.DataFrame({'specialism_code': ['A', 'A', 'B'], 'combo_vol': [10, 20, 30]})
spec_total = df.groupby('specialism_code')['combo_vol'].sum().rename('spec_vol')
print("spec_total type:", type(spec_total))
try:
    grp = df.merge(spec_total, on='specialism_code')
    print("Merged successfully")
except Exception as e:
    print(f"Merge error: {e.__class__.__name__}: {e}")
