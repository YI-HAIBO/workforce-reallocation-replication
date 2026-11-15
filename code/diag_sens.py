# -*- coding: utf-8 -*-
"""Diagnose why the interaction term is singular / nan in the double-FE panel."""
import pandas as pd, numpy as np, os
import statsmodels.api as sm
from numpy.linalg import matrix_rank

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
iaci = {"Germany":4.46,"France":3.46,"Sweden":3.41,"Italy":3.29,"Rep. Korea":3.23,
        "Spain":3.10,"Japan":2.51,"China":2.07,"Brazil":1.34,"Mexico":1.19,"United States":1.16}

def read_csv(fn):
    with open(os.path.join(BASE, fn), encoding="utf-8-sig") as f:
        return pd.read_csv(f)

com = read_csv("comtrade_robot_import.csv")[["country","year","robot_import_usd"]]
wdi = read_csv("wdi_panel.csv")
wdi["Q"] = -wdi["unemployment_pct"]
wdi = wdi[["country","year","Q","gdp_pcap_usd","urban_pct"]]

d = com.merge(wdi, on=["country","year"], how="inner")
d = d.merge(pd.DataFrame({"country":list(iaci.keys()),"IACI":list(iaci.values())}), on="country", how="inner")
d = d.rename(columns={"robot_import_usd":"AUTO"})
d["IACIxAUTO"] = d["IACI"]*d["AUTO"]

print("n=%d countries=%d years=%s" % (len(d), d["country"].nunique(), sorted(d["year"].unique())), flush=True)

# within-country demean
for v in ["Q","AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"]:
    d[v+"_dm"] = d[v] - d.groupby("country")[v].transform("mean")
# within-year demean (second stage)
for v in ["Q","AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"]:
    d[v+"_dm"] = d[v+"_dm"] - d.groupby("year")[v+"_dm"].transform("mean")

cols = ["AUTO_dm","IACIxAUTO_dm","gdp_pcap_usd_dm","urban_pct_dm"]
X = d[cols].dropna().values
print("rank of X =", matrix_rank(X), "  columns =", X.shape[1], "  rows =", X.shape[0], flush=True)

# correlation between AUTO_dm and IACIxAUTO_dm
a = d["AUTO_dm"]; b = d["IACIxAUTO_dm"]
if a.std()>0 and b.std()>0:
    print("corr(AUTO_dm, IACIxAUTO_dm) = %.6f" % np.corrcoef(a,b)[0,1], flush=True)

# Is IACIxAUTO_dm exactly = IACI * AUTO_dm within country? (it should be, since IACI time-invariant)
d["ratio"] = d["IACIxAUTO_dm"]/d["AUTO_dm"].replace(0,np.nan)
print("ratio IACIxAUTO_dm/AUTO_dm  std within country = %.8f" % d.groupby("country")["ratio"].std().max(), flush=True)
print("IACI values per country (within-country mean of IACI):", flush=True)
print(d.groupby("country")["IACI"].first().to_dict(), flush=True)

# What is the within-country within-year transform of IACI*AUTO vs AUTO?
# After country demeaning, IACIxAUTO_dm_c = IACI*(AUTO - AUTObar_c) = IACI * AUTO_dm_c  (exact)
# So the two columns are related column-by-column by country-specific scalars -> NOT globally collinear unless IACI constant.
# But check per-country rank
print("\nPer-country within-year demeaned AUTO_dm and IACIxAUTO_dm (2023 vs 2024 check):", flush=True)
for c, grp in d.groupby("country"):
    sub = grp[["year","AUTO_dm","IACIxAUTO_dm"]].sort_values("year")
    print("  %-14s " % c, sub.round(4).values.tolist(), flush=True)

# Try the regression directly and print collinearity diagnostics
dd = d.dropna(subset=["Q"]+cols+["country","year"]).copy()
Xf = sm.add_constant(dd[cols])
try:
    res = sm.OLS(dd["Q_dm"], Xf).fit()
    print("\nOLS result:", flush=True)
    print(res.params.round(6), flush=True)
    print("eigs of X'X:", flush=True)
    print(np.linalg.eigvalsh(Xf.values.T @ Xf.values), flush=True)
except Exception as e:
    print("OLS failed:", e, flush=True)
