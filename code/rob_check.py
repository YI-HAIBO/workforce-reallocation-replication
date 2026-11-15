# -*- coding: utf-8 -*-
"""IACI construction robustness using independently collected public data.
Cross-validates the paper's IACI (2024, from Figure 4) against:
  - EPL (temporary contracts, 0-6) collected via Statizoid/OECD
  - Labour-rights compliance (ILO SDG 8.8.2, 0-10) collected via OWID/ILO
Reports rank consistency (Spearman) and the sign/structure of the 2024 cross-section.
"""
import pandas as pd, numpy as np, os
from scipy import stats

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

# --- Paper IACI, 2024 snapshot (Figure 4 labels) ---
iaci = {
    "Germany": 4.46, "France": 3.46, "Sweden": 3.41, "Italy": 3.29,
    "Rep. Korea": 3.23, "Spain": 3.10, "Japan": 2.51, "China": 2.07,
    "Brazil": 1.34, "Mexico": 1.19, "United States": 1.16,
}

# --- EPL (temporary contracts, 0-6), 2024; note China/Brazil only 2008-2012 ---
epl = {}
with open(os.path.join(BASE, "epl_panel_11.csv"), encoding="utf-8-sig") as f:
    for row in pd.read_csv(f).to_dict("records"):
        if row["year"] == 2024:
            epl[row["country"]] = row["ept"]
epl_note = {c: "2024" for c in epl}
for c in ["China", "Brazil"]:
    if c not in epl:
        epl_note[c] = "none"

# --- Labour rights compliance (0-10), 2024 ---
lab = {}
with open(os.path.join(BASE, "labor_rights_11panel.csv"), encoding="utf-8-sig") as f:
    d = pd.read_csv(f)
for _, row in d.iterrows():
    lab[row["country"]] = row["y2024"]

# --- AUTO 2024 (IFR density) ---
auto = {}
with open(os.path.join(BASE, "ifr_density_2023_2024.csv"), encoding="utf-8-sig") as f:
    for row in pd.read_csv(f).to_dict("records"):
        if pd.notna(row.get("density_2024")):
            auto[row["country"]] = row["density_2024"]

# --- Q, X 2024 (WDI) ---
q = {}; gdp = {}; urb = {}
with open(os.path.join(BASE, "wdi_panel.csv"), encoding="utf-8-sig") as f:
    for row in pd.read_csv(f).to_dict("records"):
        if row["year"] == 2024:
            q[row["country"]] = row["unemployment_pct"]
            gdp[row["country"]] = row["gdp_pcap_usd"]
            urb[row["country"]] = row["urban_pct"]

countries = list(iaci.keys())
rows = []
for c in countries:
    rows.append({
        "country": c, "IACI": iaci[c],
        "EPL24": epl.get(c, np.nan), "EPL_note": epl_note.get(c, ""),
        "lab24": lab.get(c, np.nan), "AUTO24": auto.get(c, np.nan),
        "Q24_unemp": q.get(c, np.nan), "Q24": -q.get(c, np.nan),
        "gdp24": gdp.get(c, np.nan), "urb24": urb.get(c, np.nan),
    })
df = pd.DataFrame(rows).sort_values("IACI", ascending=False).reset_index(drop=True)

print("=== 11-country data matrix (2024) ===")
print(df[["country","IACI","EPL24","lab24","AUTO24","Q24_unemp","gdp24","urb24"]].round(2).to_string(index=False))

# --- Rank consistency (Spearman) among IACI, EPL, labour ---
print("\n=== Spearman rank correlations (2024, country level) ===")
pair = df.dropna(subset=["EPL24","lab24"]).copy()
if len(pair) >= 4:
    m = pair[["IACI","EPL24","lab24"]].corr(method="spearman")
    print(m.round(3).to_string())
else:
    print("insufficient EPL24 (n=%d)" % len(pair))

# EPL-only availability
print("\nEPL 2024 available for:", df["EPL24"].notna().sum(), "countries:", list(df[df['EPL24'].notna()]['country']))

# --- Rank agreement: IACI vs alternative institutional proxies ---
def rankcorr(a, b):
    a2 = df[a].rank(); b2 = df[b].rank()
    return stats.spearmanr(a2, b2).correlation

print("\n=== Rank agreement with paper IACI ===")
for col, label in [("EPL24","EPL (temporary, 0-6)"),
                   ("lab24","Labour-rights compliance (0-10)")]:
    sub = df.dropna(subset=[col])
    if len(sub) >= 4:
        rho = stats.spearmanr(sub["IACI"], sub[col]).correlation
        print("  %-30s rho=%.3f  (n=%d)" % (label, rho, len(sub)))

# --- EPL+labour combined proxy (equal-weight, min-max to 0-6) ---
sub = df.dropna(subset=["EPL24","lab24"]).copy()
if len(sub) >= 4:
    def mm(s):
        lo, hi = s.min(), s.max()
        return (s-lo)/(hi-lo)*6 if hi > lo else s*0
    sub["EPL06"] = mm(sub["EPL24"]); sub["lab06"] = mm(sub["lab24"])
    sub["proxy"] = (sub["EPL06"]+sub["lab06"])/2
    rho = stats.spearmanr(sub["IACI"], sub["proxy"]).correlation
    print("  %-30s rho=%.3f  (n=%d)" % ("EPL+labour equal-weight proxy", rho, len(sub)))
    print("  rank table:")
    t = sub[["country","IACI","proxy"]].sort_values("IACI", ascending=False)
    t["rankIACI"] = t["IACI"].rank(ascending=False).astype(int)
    t["rankProxy"] = t["proxy"].rank(ascending=False).astype(int)
    print(t[["country","IACI","proxy","rankIACI","rankProxy"]].round(2).to_string(index=False))

# --- 2024 cross-section: AUT0 vs Q, split by IACI median (descriptive) ---
print("\n=== 2024 cross-section, AUTO vs Q by IACI group (descriptive) ===")
cc = df.dropna(subset=["AUTO24","Q24"]).copy()
if len(cc) >= 8:
    med = cc["IACI"].median()
    hi = cc[cc["IACI"] >= med]; lo = cc[cc["IACI"] < med]
    for nm, grp in [("High-IACI", hi), ("Low-IACI", lo)]:
        if len(grp) >= 3 and grp["AUTO24"].nunique() > 1:
            sl, icpt = np.polyfit(grp["AUTO24"], grp["Q24"], 1)
            print("  %-10s n=%d  slope dQ/dAUTO=%.4f  meanAUTO=%.0f meanQ=%.2f" % (nm, len(grp), sl, grp["AUTO24"].mean(), grp["Q24"].mean()))
        else:
            print("  %-10s n=%d (insufficient)" % (nm, len(grp)))

df.to_csv(os.path.join(BASE, "iaci_crosscheck.csv"), index=False)
print("\nsaved iaci_crosscheck.csv")
