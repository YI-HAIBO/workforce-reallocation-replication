# -*- coding: utf-8 -*-
"""Audit: (1) Table 1 internal consistency of reallocation accounting;
   (2) Table 3 robot density vs ifr CSV; (3) Table 5 EPL vs epl_panel CSV."""
import io, csv, os

W = r"C:/Users/Yi/WorkBuddy/2026-11-12-17-50-08"
OUT = io.open(W + r"/audit_consistency.txt", "w", encoding="utf-8")

# ---------- (1) Table 1 reallocation accounting self-consistency ----------
# Table 1: Year, MfgShare, ConstrShare, TotalMigrant(100m), MfgCount(100m), Wage, MfgWage
T1 = {
    2021: (27.1, 19.0, 292.51, 79.26),
    2025: (28.2, 13.8, 301.15, 84.92),
}
OUT.write("=== (1) TABLE 1 REALLOCATION ACCOUNTING SELF-CONSISTENCY ===\n")
mfg21, cs21, tot21, cnt21 = T1[2021]
mfg25, cs25, tot25, cnt25 = T1[2025]
mfg_gain = (cnt25 - cnt21) * 1e6          # in persons
pool_gain = mfg21/100.0 * (tot25 - tot21) * 1e6
comp_gain = mfg_gain - pool_gain
gamma = 1 - (mfg21/100.0 * (tot25 - tot21) * 1e6) / mfg_gain
OUT.write(f"Mfg share: {mfg21}% -> {mfg25}%  (change {mfg25-mfg21:+.1f} pp)\n")
OUT.write(f"Constr share: {cs21}% -> {cs25}%  (change {cs25-cs21:+.1f} pp)\n")
OUT.write(f"Mfg count: {cnt21} -> {cnt25} (100m)  -> gain = {mfg_gain/1e6:.2f} mln\n")
OUT.write(f"Pool growth contribution = 0.271 x ({tot25-tot21}) = {pool_gain/1e6:.2f} mln\n")
OUT.write(f"Composition contribution = {comp_gain/1e6:.2f} mln\n")
OUT.write(f"gamma = 1 - pool_gain/mfg_gain = {gamma:.3f}\n")
OUT.write(f"PAPER says: 5.66 mln gain, 2.34 mln pool, 3.31 mln composition, gamma=0.586\n")
OUT.write(f"  gain match: {abs(mfg_gain/1e6-5.66)<0.02}; pool match: {abs(pool_gain/1e6-2.34)<0.02}; "
          f"comp match: {abs(comp_gain/1e6-3.31)<0.02}; gamma match: {abs(gamma-0.586)<0.005}\n")

# ---------- (2) Table 3 robot density vs IFR CSV ----------
OUT.write("\n=== (2) TABLE 3 ROBOT DENSITY vs ifr_robot_density_2024.csv ===\n")
paper_t3 = {"Republic of Korea":1220,"Singapore":818,"Germany":449,"Japan":446,"Sweden":377,
            "Denmark":329,"Slovenia":315,"United States":307,"Chinese Taipei":302,
            "Switzerland":294,"China":166}
csv_t3 = {}
for fn in ["ifr_robot_density_2024.csv","ifr_density_2023_2024.csv"]:
    p = os.path.join(W, fn)
    if os.path.exists(p):
        with io.open(p, encoding="utf-8") as f:
            rd = csv.DictReader(f)
            rows = list(rd)
            OUT.write(f"\n--- {fn} ({len(rows)} rows) ---\n")
            OUT.write("  header: " + ",".join(rd.fieldnames or []) + "\n")
            for r in rows[:12]:
                OUT.write("  " + str(r) + "\n")
# Try match China 166
OUT.write("\nPaper China=166; check CSV rows containing 166 or 'China'\n")

# ---------- (3) Table 5 EPL vs epl_panel_11.csv 2025 ----------
OUT.write("\n=== (3) TABLE 5 EPL (2025) vs epl_panel_11.csv ===\n")
p = os.path.join(W, "epl_panel_11.csv")
if os.path.exists(p):
    with io.open(p, encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            if str(r.get("year","")) == "2025":
                OUT.write(f"  {r.get('code','?')} {r.get('country','?')}: EPL={r.get('epl','?')}\n")
OUT.close()
print("DONE")
