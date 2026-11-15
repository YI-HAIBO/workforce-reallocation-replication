# -*- coding: utf-8 -*-
"""Multi-measure AUTO sensitivity analysis (v2, z-scored + FD for T=2).

Model:  Q_it = a + b1*IACI + b2*AUTO + b3*(IACI x AUTO) + g'X + mu_i + lam_t + e_it
Object of interest: b3 (interaction). IACI is time-invariant (Figure 4 of the paper),
so with country FE the main effect b1 is absorbed; b3 is identified through the
cross-country heterogeneity in the AUTO->Q response.

Measures of AUTO (all from public sources, all z-scored within the estimation sample so
the b3's are directly comparable across measures):
  A) IFR robot density 2023-2024 (OWID/IFR, paper-consistent units)  -- T=2 -> first-difference
  B) Comtrade HS8479.50 robot import value 2020-2024 (log)           -- double FE
  C) Comtrade import / GDP per capita (intensity proxy)              -- double FE
  D) OWID annual robot installations 2011-2024 (log, 5 countries)    -- double FE
  X) Cross-section 2024 (all three measures side by side)            -- OLS

Output: sensitivity results printed and saved to sens_results_v2.csv.
"""
import pandas as pd, numpy as np, os
import statsmodels.api as sm
from numpy.linalg import matrix_rank

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
iaci = {"Germany":4.46,"France":3.46,"Sweden":3.41,"Italy":3.29,"Rep. Korea":3.23,
        "Spain":3.10,"Japan":2.51,"China":2.07,"Brazil":1.34,"Mexico":1.19,"United States":1.16}

def read_csv(fn):
    with open(os.path.join(BASE, fn), encoding="utf-8-sig") as f:
        return pd.read_csv(f)

def zscore(s):
    s = s.astype(float)
    return (s - s.mean()) / s.std()

def make_iaci():
    """IACI as a DataFrame; returns country and standardized IACI (z) and raw."""
    d = pd.DataFrame({"country": list(iaci.keys()), "IACI_raw": list(iaci.values())})
    d["IACI"] = zscore(d["IACI_raw"])
    return d

# ---------- load ----------
ifr = read_csv("ifr_density_2023_2024.csv")
com = read_csv("comtrade_robot_import.csv")[["country","year","robot_import_usd"]]
wdi = read_csv("wdi_panel.csv")
wdi["Q"] = -wdi["unemployment_pct"]
wdi = wdi[["country","year","Q","gdp_pcap_usd","urban_pct"]]
ins = read_csv("owid_robots_installed.csv")
ins.columns = ["entity","code","year","installs"]
ins["country"] = ins["code"].map({"CHN":"China","DEU":"Germany","JPN":"Japan","KOR":"Rep. Korea","USA":"United States"})
ins = ins.dropna(subset=["country"])

iaci_df = make_iaci()

results = []  # list of dicts

# ---------- generic double-FE regression ----------
def fe_reg(data, autoname, label, use_log=False, fd=False):
    """Double-country-year FE (or first-difference if fd=True) on z-scored AUTO.
    Regressors: AUTO_z, IACI_z x AUTO_z (interaction), gdp_pcap, urban_pct.
    Returns dict of b3 stats."""
    d = data.copy()
    d = d.merge(iaci_df, on="country", how="inner")
    d = d.dropna(subset=["Q", autoname, "gdp_pcap_usd", "urban_pct"])
    if len(d) < 8:
        return {"label": label, "n": len(d), "countries": d["country"].nunique() if len(d) else 0, "note": "insufficient"}
    d["AUTO"] = d[autoname].astype(float)
    if use_log:
        d["AUTO"] = np.log(d["AUTO"].clip(lower=1e-6))
    d["AUTO"] = zscore(d["AUTO"])
    d["IACIxAUTO"] = d["IACI"] * d["AUTO"]

    if fd:
        # first-difference within country (T=2 or unbalanced -> use diff)
        d = d.sort_values(["country","year"])
        d["dQ"] = d.groupby("country")["Q"].diff()
        d["dAUTO"] = d.groupby("country")["AUTO"].diff()
        d["dIACIxAUTO"] = d.groupby("country")["IACIxAUTO"].diff()
        d["dgdp"] = d.groupby("country")["gdp_pcap_usd"].diff()
        d["durban"] = d.groupby("country")["urban_pct"].diff()
        dd = d.dropna(subset=["dQ","dAUTO","dIACIxAUTO"])
        dd = dd[dd["dQ"].abs() > 0]  # drop zero-change rows (no info)
        if len(dd) < 6:
            return {"label": label, "n": len(dd), "countries": dd["country"].nunique() if len(dd) else 0, "note": "insufficient(FD)"}
        X = sm.add_constant(dd[["dAUTO","dIACIxAUTO","dgdp","durban"]])
        res = sm.OLS(dd["dQ"], X).fit()
        key = "dIACIxAUTO"
    else:
        # double demean (country then year)
        for v in ["Q","AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"]:
            d[v+"_dm"] = d[v] - d.groupby("country")[v].transform("mean")
        for v in ["Q","AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"]:
            d[v+"_dm"] = d[v+"_dm"] - d.groupby("year")[v+"_dm"].transform("mean")
        dd = d.dropna(subset=["Q_dm","AUTO_dm","IACIxAUTO_dm","gdp_pcap_usd_dm","urban_pct_dm"])
        X = sm.add_constant(dd[["AUTO_dm","IACIxAUTO_dm","gdp_pcap_usd_dm","urban_pct_dm"]])
        res = sm.OLS(dd["Q_dm"], X).fit()
        key = "IACIxAUTO_dm"

    b3 = float(res.params[key]); se3 = float(res.bse[key])
    t3 = float(res.tvalues[key]); p3 = float(res.pvalues[key])
    r2 = float(res.rsquared)
    return {"label": label, "n": len(dd), "countries": dd["country"].nunique(),
            "b3": b3, "se": se3, "t": t3, "p": p3, "r2": r2,
            "sign": "POS" if b3 > 0 else "NEG", "sig": p3 < 0.05,
            "note": "FD" if fd else "doubleFE"}

# ---------- Panel A: IFR density 2023-2024 (T=2, first-difference) ----------
ifr_long = []
for _, r in ifr.iterrows():
    for col, yr in [("density_2023",2023),("density_2024",2024)]:
        if pd.notna(r.get(col)):
            ifr_long.append({"country": r["country"], "year": yr, "AUTO_ifr": r[col]})
ifr_long = pd.DataFrame(ifr_long)
A = ifr_long.merge(wdi, on=["country","year"], how="inner")
rA = fe_reg(A, "AUTO_ifr", "A) IFR density 23-24 (FD)", use_log=False, fd=True)
results.append(rA)

# ---------- Panel B: Comtrade import value (log, double FE) ----------
B = com.merge(wdi, on=["country","year"], how="inner")
rB = fe_reg(B, "robot_import_usd", "B) Comtrade import (log, dFE)", use_log=True, fd=False)
results.append(rB)

# ---------- Panel C: import / GDP per capita ----------
C = com.merge(wdi, on=["country","year"], how="inner")
C["impgdp"] = C["robot_import_usd"] / C["gdp_pcap_usd"]
rC = fe_reg(C, "impgdp", "C) import/GDPpcap (dFE)", use_log=False, fd=False)
results.append(rC)

# ---------- Panel D: installs 2011-2024 (log, double FE, 5 countries) ----------
D = ins.merge(wdi, on=["country","year"], how="inner")
rD = fe_reg(D, "installs", "D) installs (log, dFE, 5c)", use_log=True, fd=False)
results.append(rD)

# ---------- Cross-section 2024 ----------
def cross_reg(data, autoname, label, use_log=False):
    d = data[data["year"]==2024].copy()
    d = d.merge(iaci_df, on="country", how="inner")
    d = d.dropna(subset=["Q", autoname])
    if len(d) < 6:
        return {"label": label, "n": len(d), "countries": d["country"].nunique() if len(d) else 0, "note": "insufficient"}
    d["AUTO"] = d[autoname].astype(float)
    if use_log:
        d["AUTO"] = np.log(d["AUTO"].clip(lower=1e-6))
    d["AUTO"] = zscore(d["AUTO"])
    d["IACIxAUTO"] = d["IACI"] * d["AUTO"]
    X = sm.add_constant(d[["AUTO","IACIxAUTO"]])
    res = sm.OLS(d["Q"], X).fit()
    key = "IACIxAUTO"
    b3 = float(res.params[key]); se3 = float(res.bse[key]); t3 = float(res.tvalues[key]); p3 = float(res.pvalues[key])
    return {"label": label, "n": len(d), "countries": d["country"].nunique(),
            "b3": b3, "se": se3, "t": t3, "p": p3, "r2": float(res.rsquared),
            "sign": "POS" if b3>0 else "NEG", "sig": p3<0.05, "note": "crosssec2024"}

c2024 = wdi.copy()
c2024 = c2024.merge(ifr_long[ifr_long["year"]==2024][["country","AUTO_ifr"]], on=["country"], how="left")
c2024 = c2024.merge(com[com["year"]==2024][["country","robot_import_usd"]], on=["country"], how="left")
c2024["impgdp"] = c2024["robot_import_usd"] / c2024["gdp_pcap_usd"]
results.append(cross_reg(c2024, "AUTO_ifr", "X1) IFR density 2024 (CS)", use_log=False))
results.append(cross_reg(c2024, "robot_import_usd", "X2) Comtrade import 2024 (CS, log)", use_log=True))
results.append(cross_reg(c2024, "impgdp", "X3) import/GDPpcap 2024 (CS)", use_log=False))

# ---------- report ----------
print("="*100)
print("MULTI-MEASURE AUTO SENSITIVITY  (Q = -unemployment; IACI = paper Figure 4, z-scored;")
print("  interaction beta3 = IACI_z x AUTO_z; positive beta3 = higher IACI amplifies automation->Q)")
print("="*100)
print("%-38s %4s %4s %10s %9s %7s %7s %6s %6s %5s" % ("measure","n","c","beta3","se","t","p","R2","sign","sig"))
print("-"*100)
for r in results:
    if "note" in r and "b3" not in r:
        print("%-38s %4s %4s  -- %s" % (r["label"], r.get("n","-"), r.get("countries","-"), r["note"]))
    else:
        print("%-38s %4d %4d %10.5f %9.5f %7.3f %7.4f %6.3f %6s %5s" %
              (r["label"], r["n"], r["countries"], r["b3"], r["se"], r["t"], r["p"], r["r2"], r["sign"], "***" if r["sig"] else ""))

# paper baseline for reference
print("-"*100)
print("PAPER BASELINE (full 2000-2024 panel, IFR density, natural units): beta3 = 0.054*** (p=0.0002),")
print("  wild-cluster bootstrap 95% CI [0.021, 0.088]. Positive & significant.")
print("="*100)

# save
out = pd.DataFrame(results)
out.to_csv(os.path.join(BASE, "sens_results_v2.csv"), index=False)
print("\nsaved sens_results_v2.csv  (%d rows)" % len(out))
