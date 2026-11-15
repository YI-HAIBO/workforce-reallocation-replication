# -*- coding: utf-8 -*-
"""L34 核心推进：真实 2020-24 面板（11 国×5 年）双固定效应交互回归。
注意：IACI 的 EPL 成分此处采用 epl_panel_11.csv 的 ept 列，即 OECD 临时合同保护严格度（EPT），
并非整体 EPL 指数（口径错配，见数据与代码审计报告 2026-11-15 发现 F7）。
AUTO = Comtrade 机器人进口（真实）；IACI = 真实时间变化双成分（EPL+劳动权利）；
Q = 失业率；控制 GDP/urban。z-score 防病态。wild-cluster bootstrap 推断。
"""
import csv, os, numpy as np

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
def load_rows(p):
    with open(p, encoding="utf-8-sig") as f: return list(csv.DictReader(f))

# ---- 真实数据 ----
imp = {}
for r in load_rows(os.path.join(BASE,"comtrade_robot_import.csv")):
    try:
        imp[(r["code"].strip(), int(r["year"]))] = float(r["robot_import_usd"])
    except Exception:
        pass

epl = {}
for r in load_rows(os.path.join(BASE,"epl_panel_11.csv")):
    try: epl[(r["iso3"].strip(), int(r["year"]))] = float(r["ept"])
    except Exception: pass

lr = {}
for r in load_rows(os.path.join(BASE,"labor_rights_11panel.csv")):
    c = r["code"].strip()
    for y in range(2015,2025):
        try: lr[(c,y)] = float(r[f"y{y}"])
        except Exception: pass

wdi = {}
for r in load_rows(os.path.join(BASE,"wdi_panel.csv")):
    try: wdi[(r["country_code"].strip(), int(r["year"]))] = r
    except Exception: pass

NAME = {"276":"Germany","250":"France","752":"Sweden","380":"Italy","410":"Rep. Korea",
        "724":"Spain","392":"Japan","156":"China","76":"Brazil","484":"Mexico","842":"United States","699":"India"}
# 国家码映射: Comtrade code -> iso3
CODE3 = {"276":"DEU","250":"FRA","752":"SWE","380":"ITA","410":"KOR","724":"ESP",
         "392":"JPN","156":"CHN","76":"BRA","484":"MEX","842":"USA","699":"IND"}

rows = []
for (c, y) in sorted(imp.keys()):
    c3 = CODE3.get(c)
    if c3 is None: continue
    if (c3,y) not in epl or (c3,y) not in lr or (c3,y) not in wdi: continue
    w = wdi[(c3,y)]
    try:
        rows.append({"code":c3,"name":NAME[c],"year":y,
                     "imp": imp[(c,y)], "ept": epl[(c3,y)], "lr": lr[(c3,y)],
                     "unemp": float(w["unemployment_pct"]), "gdp": float(w["gdp_pcap_usd"]),
                     "urban": float(w["urban_pct"])})
    except Exception:
        continue

print(f"真实面板：{len(rows)} 行 = {len(set(r['code'] for r in rows))} 国 × {len(set(r['year'] for r in rows))} 年")
countries = sorted(set(r['code'] for r in rows))
years = sorted(set(r['year'] for r in rows))
print(f"  国家: {', '.join(NAME.get(c,c) for c in countries)}")
print(f"  年份: {years}")

# ---- IACI 时间变化（固定界限归一化，0-6）----
all_e = np.array([r["ept"] for r in rows]); all_l = np.array([r["lr"] for r in rows])
e_lo,e_hi = all_e.min(), all_e.max(); l_lo,l_hi = all_l.min(), all_l.max()
def iaci(e,l): return ((e-e_lo)/(e_hi-e_lo) + (l-l_lo)/(l_hi-l_lo))/2*6
for r in rows:
    r["iaci"] = iaci(r["ept"], r["lr"])

# ---- 双固定效应（within: 国家+年份去均值）----
def within(v, idx_c, idx_y):
    v = np.array(v, float)
    # 去国家均值
    for c in set(idx_c):
        m = [i for i,x in enumerate(idx_c) if x==c]
        v[m] -= np.mean(v[m])
    # 去年份均值
    for y in set(idx_y):
        m = [i for i,x in enumerate(idx_y) if x==y]
        v[m] -= np.mean(v[m])
    return v

def zs(v):
    v=np.array(v,float); s=v.std()
    return (v-v.mean())/s if s>0 else v

import statsmodels.api as sm

idx_c = [r["code"] for r in rows]; idx_y = [r["year"] for r in rows]
def run_fe(Qv, dep_label):
    # 双去均值后 z-score
    Qd = within(Qv, idx_c, idx_y)
    Id = within([r["iaci"] for r in rows], idx_c, idx_y)
    Ad = within([r["imp"] for r in rows], idx_c, idx_y)
    Gd = within([r["gdp"] for r in rows], idx_c, idx_y)
    Ud = within([r["urban"] for r in rows], idx_c, idx_y)
    zQ, zI, zA = zs(Qd), zs(Id), zs(Ad)
    zIA = zs(np.array(Id)*np.array(Ad))
    zG, zU = zs(Gd), zs(Ud)
    Xc = sm.add_constant(np.column_stack([zI, zA, zIA]))
    m = sm.OLS(zQ, Xc).fit()
    Xc2 = sm.add_constant(np.column_stack([zI, zA, zIA, zG, zU]))
    m2 = sm.OLS(zQ, Xc2).fit()
    print(f"\n[{dep_label}] 双固定效应，z-score，n={len(rows)}，{len(set(idx_c))} 国×{len(set(idx_y))} 年")
    print(f"  无控制: β1(IACI)={m.params[1]:+.3f}  β2(AUTO)={m.params[2]:+.3f}  β3(IACI×AUTO)={m.params[3]:+.3f} (se={m.bse[3]:.3f}, p={m.pvalues[3]:.3f})")
    print(f"  含GDP/urban: β1={m2.params[1]:+.3f}  β2={m2.params[2]:+.3f}  β3={m2.params[3]:+.3f} (se={m2.bse[3]:.3f}, p={m2.pvalues[3]:.3f})")
    return m, m2

print("\n"+"="*80)
print("L34 推进：真实 2020-24 面板双固定效应交互回归")
print("="*80)
unemp = [r["unemp"] for r in rows]
m1, m1c = run_fe(unemp, "Q=失业率(论文 Q 口径相反)")
print("\n  [注] 论文 Q=负失业率 -> 论文 β3>0 对应本表失业率 β3<0")

# ---- wild-cluster bootstrap（1000 次 Rademacher，聚类国家）----
print("\n--- wild-cluster bootstrap β3（聚类国家，1000 次 Rademacher）---")
rng = np.random.default_rng(20261115)
Qd = within(unemp, idx_c, idx_y)
Id = within([r["iaci"] for r in rows], idx_c, idx_y)
Ad = within([r["imp"] for r in rows], idx_c, idx_y)
Gd = within([r["gdp"] for r in rows], idx_c, idx_y)
Ud = within([r["urban"] for r in rows], idx_c, idx_y)
zQ, zI, zA = zs(Qd), zs(Id), zs(Ad)
zIA = zs(np.array(Id)*np.array(Ad))
zG, zU = zs(Gd), zs(Ud)
X = sm.add_constant(np.column_stack([zI, zA, zIA, zG, zU]))
m0 = sm.OLS(zQ, X).fit()
resid = np.array(m0.resid)
b3_hat = m0.params[3]
# 残差 bootstrap（wild, 国家聚类符号）
countries_list = sorted(set(idx_c))
b3s = []
for _ in range(1000):
    signs = {c: rng.choice([-1.0, 1.0]) for c in countries_list}
    w = np.array([signs[c] for c in idx_c])
    yb = np.array(m0.fittedvalues) + w*resid
    mb = sm.OLS(yb, X).fit()
    b3s.append(mb.params[3])
b3s = np.array(b3s)
ci = np.percentile(b3s, [2.5, 97.5])
print(f"  β3={b3_hat:+.3f}, 95% wild-CI [{ci[0]:+.3f}, {ci[1]:+.3f}], "
      f"p={float((np.sum(np.abs(b3s)>=abs(b3_hat))+1)/(1000+1)):.3f}")

# ---- 分年度/留一国家稳健 ----
print("\n--- 留一国家稳健（含控制，β3）---")
for drop in countries_list:
    keep = [i for i,c in enumerate(idx_c) if c!=drop]
    Qd2 = within([unemp[i] for i in keep], [idx_c[i] for i in keep], [idx_y[i] for i in keep])
    Id2 = within([rows[i]["iaci"] for i in keep], [idx_c[i] for i in keep], [idx_y[i] for i in keep])
    Ad2 = within([rows[i]["imp"] for i in keep], [idx_c[i] for i in keep], [idx_y[i] for i in keep])
    Gd2 = within([rows[i]["gdp"] for i in keep], [idx_c[i] for i in keep], [idx_y[i] for i in keep])
    Ud2 = within([rows[i]["urban"] for i in keep], [idx_c[i] for i in keep], [idx_y[i] for i in keep])
    Xc = sm.add_constant(np.column_stack([zs(Id2), zs(Ad2), zs(np.array(Id2)*np.array(Ad2)), zs(Gd2), zs(Ud2)]))
    mb = sm.OLS(zs(Qd2), Xc).fit()
    print(f"  去掉{NAME.get(drop,drop):<12} β3={mb.params[3]:+.3f} (p={mb.pvalues[3]:.3f})")

print("\nDONE")
