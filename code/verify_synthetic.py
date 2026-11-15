# -*- coding: utf-8 -*-
"""Definitive data-governance verification of the C-version l2_data panel.

Findings to verify:
  1) Are ALL series in the C-version panel synthetic (constant-difference linear ramps)?
  2) Does the C-version panel reproduce the paper's interaction beta3? (expected: NO, because
     all within-country variation is arithmetic backfill, so the interaction is not identified
     on genuine variation.)
  3) Is the paper's beta3=0.054 reproducible from any REAL independent data available locally?
     -> IFR 2023-24 density (OWID-verified), paper IACI (Figure 4), WDI Q/X. Cross-section + FD.
"""
import pandas as pd, numpy as np, os
import statsmodels.api as sm

D = r"E:\task\论文：Directional Evidence on Workforce Reallocation in China's\2026-10-07_C_version\l2_data"
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
def ld(fn): return pd.read_excel(os.path.join(D,fn)) if fn.endswith("xlsx") else pd.read_csv(os.path.join(D,fn))

print("="*90)
print("PART 1 - Synthetic-detection: is every series a constant-difference ramp?")
print("="*90)
files = [("ifr_rodensity.xlsx","ROB"),("oecd_epl.xlsx","EPL"),
         ("oecd_woreplacement.xlsx","WREPL"),("ilo_codetermination.csv","COD")]
synth_total = 0; real_total = 0
for fn, col in files:
    df = ld(fn)
    print("\n  %s (%s): %d countries x %d yrs" % (fn, col, df['country'].nunique(), df['year'].nunique()))
    for c in sorted(df['country'].unique()):
        g = df[df['country']==c].sort_values('year')[['year',col]].dropna()
        if len(g) < 3: continue
        vals = g[col].tolist()
        diffs = np.round(np.diff(vals), 6)
        constant = np.allclose(diffs, diffs[0], atol=1e-6)  # constant diff = pure linear ramp
        synth_total += constant; real_total += (not constant)
        if c in ("China","Germany","US"):
            print("    %-10s n=%2d  const_diff=%s  first=%.3f last=%.3f  step=%.4f" %
                  (c, len(vals), constant, vals[0], vals[-1], diffs[0]))
print("\n  >>> synthetic (linear-ramp) series: %d  |  genuinely-varying series: %d  (of %d checked)"
      % (synth_total, real_total, synth_total+real_total))

print("\n"+"="*90)
print("PART 2 - Can the C-version panel reproduce beta3? (double-FE interaction)")
print("="*90)
# build C-version panel from the 4 synthetic series + unemployment is NOT in real countries
# -> use WDI unemployment for the countries that overlap
sub = ld("ifr_rodensity.xlsx")[["country","year","ROB"]]
for fn, col in [("oecd_epl.xlsx","EPL"),("oecd_woreplacement.xlsx","WREPL"),("ilo_codetermination.csv","COD")]:
    sub = sub.merge(ld(fn)[["country","year",col]], on=["country","year"])
wdi = pd.read_csv(os.path.join(BASE,"wdi_panel.csv"), encoding="utf-8-sig")
wdi["Q"] = -wdi["unemployment_pct"]
# map C-version names -> WDI names
m = {"Korea":"Rep. Korea","US":"United States","UK":"United Kingdom"}
sub["cw"] = sub["country"].map(lambda x: m.get(x,x))
pan = sub.merge(wdi[["country","year","Q","gdp_pcap_usd","urban_pct"]],
                left_on=["cw","year"], right_on=["country","year"], how="inner")
pan = pan.dropna(subset=["ROB","EPL","WREPL","COD","Q"])
print("  C-version panel merged with WDI: n=%d, countries=%d, years=%s"
      % (len(pan), pan['cw'].nunique(), sorted(pan['year'].unique())[:2]))

# 0-6 min-max normalize + equal-weight IACI (paper construction)
def mm(s):
    lo,hi=s.min(),s.max(); return (s-lo)/(hi-lo)*6 if hi>lo else s*0
for c in ["EPL","WREPL","COD"]:
    pan[c+"_06"]=mm(pan[c].astype(float))
pan["IACI"] = (pan["EPL_06"]+pan["WREPL_06"]+pan["COD_06"])/3
pan["AUTO"]=pan["ROB"].astype(float)
pan["IACIxAUTO"]=pan["IACI"]*pan["AUTO"]

def fe(data, y, xv, unit="country", time="year"):
    dd=data.dropna(subset=[y]+xv+[unit,time]).copy()
    for v in [y]+xv:
        dd[v+"_dm"]=dd[v]-dd.groupby(unit)[v].transform("mean")
    for v in [y]+xv:
        dd[v+"_dm"]=dd[v+"_dm"]-dd.groupby(time)[v+"_dm"].transform("mean")
    X=sm.add_constant(dd[[v+"_dm" for v in xv]])
    return sm.OLS(dd[y+"_dm"],X).fit(), len(dd)
res,n = fe(pan,"Q",["AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"], unit="cw")
b3=res.params.get("IACIxAUTO",np.nan); p3=res.pvalues.get("IACIxAUTO",np.nan)
print("  C-version panel double-FE:  beta3=%.5f  p=%.4f  n=%d" % (b3,p3,n))
print("  (NOTE: ROB/EPL/WREPL/COD are all linear ramps -> within-country variation is pure arithmetic)")

print("\n"+"="*90)
print("PART 3 - Real-data reproduction (genuine variation only): 2023-24 IFR density + paper IACI")
print("="*90)
iaci = {"Germany":4.46,"France":3.46,"Sweden":3.41,"Italy":3.29,"Rep. Korea":3.23,
        "Spain":3.10,"Japan":2.51,"China":2.07,"Brazil":1.34,"Mexico":1.19,"United States":1.16}
ifr = pd.read_csv(os.path.join(BASE,"ifr_density_2023_2024.csv"), encoding="utf-8-sig")
long=[]
for _,r in ifr.iterrows():
    for col,yr in [("density_2023",2023),("density_2024",2024)]:
        if pd.notna(r.get(col)): long.append({"country":r["country"],"year":yr,"AUTO":r[col]})
long=pd.DataFrame(long)
pan2 = long.merge(wdi[["country","year","Q","gdp_pcap_usd","urban_pct"]],on=["country","year"],how="inner")
pan2 = pan2.merge(pd.DataFrame({"country":list(iaci.keys()),"IACI":list(iaci.values())}),on="country")
pan2["IACIxAUTO"]=pan2["IACI"]*pan2["AUTO"]
# FD (T=2 -> first difference)
pan2=pan2.sort_values(["country","year"])
for v in ["Q","AUTO","IACIxAUTO","gdp_pcap_usd","urban_pct"]:
    pan2["d"+v]=pan2.groupby("country")[v].diff()
fd=pan2.dropna(subset=["dQ","dAUTO","dIACIxAUTO"])
fd=fd[fd["dQ"].abs()>0]
if len(fd)>=6:
    X=sm.add_constant(fd[["dAUTO","dIACIxAUTO","dgdp_pcap_usd","durban_pct"]])
    r=sm.OLS(fd["dQ"],X).fit()
    print("  Real IFR 2023-24, first-difference:  beta3=%.5f  p=%.4f  n=%d  sign=%s"
          % (r.params["dIACIxAUTO"], r.pvalues["dIACIxAUTO"], len(fd),
             "POS" if r.params["dIACIxAUTO"]>0 else "NEG"))
# 2024 cross-section
cs=pan2[pan2["year"]==2024].copy()
if len(cs)>=6:
    X=sm.add_constant(cs[["AUTO","IACIxAUTO"]])
    r=sm.OLS(cs["Q"],X).fit()
    print("  Real IFR 2024, cross-section:       beta3=%.5f  p=%.4f  n=%d  sign=%s"
          % (r.params["IACIxAUTO"], r.pvalues["IACIxAUTO"], len(cs),
             "POS" if r.params["IACIxAUTO"]>0 else "NEG"))
print("\n  PAPER: beta3 = 0.054*** (p=0.0002), wild-cluster CI [0.021,0.088]")
