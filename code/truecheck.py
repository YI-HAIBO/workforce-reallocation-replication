# -*- coding: utf-8 -*-
"""Independent re-check of the moderation direction using ONLY independently collected real data:
  - Q, X: World Bank WDI (real, 2024)
  - AUTO: IFR density 2024 via OWID (real)
  - IACI: paper's 2024 index values (Figure 4)
  - substitutes: temporary-EPL (Statizoid/OECD), labour-rights compliance (OWID/ILO)
The paper reports beta3 = +0.054 (p=0.0002). We check the sign of the interaction on real data.
"""
import pandas as pd, numpy as np, os
import statsmodels.api as sm

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

iaci = {"Germany":4.46,"France":3.46,"Sweden":3.41,"Italy":3.29,"Rep. Korea":3.23,
        "Spain":3.10,"Japan":2.51,"China":2.07,"Brazil":1.34,"Mexico":1.19,"United States":1.16}

def get_panel(fn, val):
    out = {}
    with open(os.path.join(BASE, fn), encoding="utf-8-sig") as f:
        for r in pd.read_csv(f).to_dict("records"):
            if r["year"]==2024:
                out[r["country"]] = r[val]
    return out

q = get_panel("wdi_panel.csv","unemployment_pct")
gdp = get_panel("wdi_panel.csv","gdp_pcap_usd")
urb = get_panel("wdi_panel.csv","urban_pct")
auto = {}
with open(os.path.join(BASE,"ifr_density_2023_2024.csv"), encoding="utf-8-sig") as f:
    for r in pd.read_csv(f).to_dict("records"):
        if pd.notna(r.get("density_2024")): auto[r["country"]] = r["density_2024"]
epl = get_panel("epl_panel_11.csv","ept")
lab = {}
with open(os.path.join(BASE,"labor_rights_11panel.csv"), encoding="utf-8-sig") as f:
    for r in pd.read_csv(f).to_dict("records"):
        lab[r["country"]] = r["y2024"]

rows = []
for c in iaci:
    if c in auto and c in q:
        rows.append({"country":c,"IACI":iaci[c],"AUTO":auto[c],"Q":-q[c],
                     "GDP":gdp.get(c,np.nan),"URB":urb.get(c,np.nan),
                     "EPL":epl.get(c,np.nan),"LAB":lab.get(c,np.nan)})
df = pd.DataFrame(rows)
print("sample (real data, 2024): N=", len(df), " countries:", list(df["country"]))

def cross_reg(data, idxname, label):
    dd = data.dropna(subset=[idxname]).copy()
    if len(dd) < 6:
        print("  %-28s insufficient n=%d" % (label, len(dd))); return
    dd["INTER"] = dd[idxname]*dd["AUTO"]
    X = sm.add_constant(dd[["IACI" if idxname!="IACI" else "IACI","AUTO","INTER"] if idxname=="IACI" else [idxname,"AUTO","INTER"]])
    # use the chosen index column
    X = sm.add_constant(dd[[idxname,"AUTO","INTER"]])
    mod = sm.OLS(dd["Q"], X).fit()
    b3 = mod.params.get("INTER", np.nan); p3 = mod.pvalues.get("INTER", np.nan)
    t3 = mod.tvalues.get("INTER", np.nan)
    print("  %-28s n=%2d  beta3=%8.4f  t=%6.3f  p=%.4f   (sign: %s)" %
          (label, len(dd), b3, t3, p3, "POSITIVE" if b3>0 else "NEGATIVE"))

print("\n=== 2024 cross-section interaction (real data) ===")
print("Baseline: Q ~ IACI + AUTO + IACI x AUTO")
cross_reg(df, "IACI", "IACI (paper)")
print("Substitutes:")
cross_reg(df, "EPL", "IACI -> temporary-EPL")
cross_reg(df, "LAB", "IACI -> labour-rights")

# scaled substitutes to 0-6 for comparability
def mm(s):
    lo,hi=s.min(),s.max(); return (s-lo)/(hi-lo)*6 if hi>lo else s*0
df["EPL06"] = mm(df["EPL"]); df["LAB06"] = mm(df["LAB"])
print("\n=== substitutes rescaled to 0-6 ===")
cross_reg(df, "EPL06", "IACI -> EPL06 (0-6)")
cross_reg(df, "LAB06", "IACI -> LAB06 (0-6)")

df.to_csv(os.path.join(BASE,"truecheck_2024.csv"), index=False)
print("\nsaved truecheck_2024.csv")
