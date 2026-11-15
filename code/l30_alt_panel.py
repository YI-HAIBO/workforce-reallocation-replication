# -*- coding: utf-8 -*-
"""L30 替代方案 A1：EPL-only IACI 的 2020-2025 六年面板（不依赖 SDG8.8.2）。
注意：EPL-only 实际为临时合同保护严格度（EPT）单成分，口径非整体 EPL（见审计报告 F7）。
AUTO = Comtrade 机器人进口（2025 已采集）；IACI = EPL 严格度单成分（已至 2025）；
Q = 失业率（论文 Q=负失业率，方向相反）；控制 GDP/urban（WDI 2025 已采集）。
双固定效应（国家+年份去均值）+ z-score + wild-cluster bootstrap。
对比：2020-2024（EPL-only） vs 2020-2025（EPL-only 延伸）。"""
import csv, os, numpy as np
import statsmodels.api as sm

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
def load_rows(p):
    with open(os.path.join(BASE,p), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

imp = {}
for r in load_rows("comtrade_robot_import.csv"):
    try: imp[(r["code"].strip(), int(r["year"]))] = float(r["robot_import_usd"])
    except Exception: pass

epl = {}
for r in load_rows("epl_panel_11.csv"):
    if not r["iso3"].strip(): continue
    try: epl[(r["iso3"].strip(), int(r["year"]))] = float(r["ept"])
    except Exception: pass

wdi = {}
for r in load_rows("wdi_panel.csv"):
    try: wdi[(r["country_code"].strip(), int(r["year"]))] = r
    except Exception: pass

CODE3 = {"276":"DEU","250":"FRA","752":"SWE","380":"ITA","410":"KOR","724":"ESP",
         "392":"JPN","156":"CHN","76":"BRA","484":"MEX","842":"USA"}
NAME = {v:k for k,v in CODE3.items()}

# EPL-only 面板：需 imp + epl + wdi（不要求 labor_rights）
rows = []
for (c, y) in sorted(imp.keys()):
    c3 = CODE3.get(c)
    if c3 is None: continue
    if y < 2020: continue
    if (c3,y) not in epl: continue
    if (c3,y) not in wdi: continue
    w = wdi[(c3,y)]
    try:
        rows.append({"code":c3,"name":NAME[c3],"year":y,
                     "imp": imp[(c,y)], "ept": epl[(c3,y)],
                     "unemp": float(w["unemployment_pct"]), "gdp": float(w["gdp_pcap_usd"]),
                     "urban": float(w["urban_pct"])})
    except Exception:
        continue

print(f"EPL-only 面板：{len(rows)} 行 = {len(set(r['code'] for r in rows))} 国 × {len(set(r['year'] for r in rows))} 年")
countries = sorted(set(r["code"] for r in rows))
years = sorted(set(r["year"] for r in rows))
print(f"  国家: {', '.join(NAME.get(c,c) for c in countries)}")
print(f"  年份: {years}")

# IACI = EPL 单成分归一化 0-6（pooled 2020-2025 min/max）
all_e = np.array([r["ept"] for r in rows], float)
e_lo, e_hi = all_e.min(), all_e.max()
for r in rows:
    r["iaci"] = (r["ept"] - e_lo)/(e_hi - e_lo)*6

def within(v, idx_c, idx_y):
    v = np.array(v, float)
    for c in set(idx_c):
        m = [i for i,x in enumerate(idx_c) if x==c]; v[m] -= np.mean(v[m])
    for y in set(idx_y):
        m = [i for i,x in enumerate(idx_y) if x==y]; v[m] -= np.mean(v[m])
    return v
def zs(v):
    v=np.array(v,float); s=v.std()
    return (v-v.mean())/s if s>0 else v

idx_c = [r["code"] for r in rows]; idx_y = [r["year"] for r in rows]

def run_fe(sub_rows, label):
    ic=[r["code"] for r in sub_rows]; iy=[r["year"] for r in sub_rows]
    Qd = within([r["unemp"] for r in sub_rows], ic, iy)
    Id = within([r["iaci"] for r in sub_rows], ic, iy)
    Ad = within([r["imp"] for r in sub_rows], ic, iy)
    Gd = within([r["gdp"] for r in sub_rows], ic, iy)
    Ud = within([r["urban"] for r in sub_rows], ic, iy)
    zQ,zI,zA = zs(Qd),zs(Id),zs(Ad); zIA=zs(np.array(Id)*np.array(Ad)); zG,zU=zs(Gd),zs(Ud)
    Xc = sm.add_constant(np.column_stack([zI,zA,zIA]))
    m = sm.OLS(zQ,Xc).fit()
    Xc2 = sm.add_constant(np.column_stack([zI,zA,zIA,zG,zU]))
    m2 = sm.OLS(zQ,Xc2).fit()
    print(f"\n[{label}] EPL-only IACI, n={len(sub_rows)}, {len(set(ic))}国×{len(set(iy))}年")
    print(f"  无控制: β3(IACI×AUTO)={m.params[3]:+.3f} (se={m.bse[3]:.3f}, p={m.pvalues[3]:.3f})")
    print(f"  含GDP/urban: β3={m2.params[3]:+.3f} (se={m2.bse[3]:.3f}, p={m2.pvalues[3]:.3f})")
    return m2

print("\n"+"="*78)
print("L30 替代 A1：EPL-only IACI 2020-2025 窗口延伸")
print("="*78)
m_full = run_fe(rows, "A1a 全窗口 2020-2025 (EPL-only IACI)")

# 仅 2020-2024 子集（与主窗口一致，验证可比性）
sub24 = [r for r in rows if r["year"]<=2024]
m_24 = run_fe(sub24, "A1b 主窗口 2020-2024 (EPL-only IACI)")

# ---- wild-cluster bootstrap β3（含控制，聚类国家）----
print("\n--- wild-cluster bootstrap β3（聚类国家，含 GDP/urban）---")
Qd = within([r["unemp"] for r in rows], idx_c, idx_y)
Id = within([r["iaci"] for r in rows], idx_c, idx_y)
Ad = within([r["imp"] for r in rows], idx_c, idx_y)
Gd = within([r["gdp"] for r in rows], idx_c, idx_y)
Ud = within([r["urban"] for r in rows], idx_c, idx_y)
zQ,zI,zA = zs(Qd),zs(Id),zs(Ad); zIA=zs(np.array(Id)*np.array(Ad)); zG,zU=zs(Gd),zs(Ud)
X = sm.add_constant(np.column_stack([zI,zA,zIA,zG,zU]))
m0 = sm.OLS(zQ,X).fit()
resid=np.array(m0.resid); b3_hat=m0.params[3]
rng=np.random.default_rng(20261115)
clist=sorted(set(idx_c)); b3s=[]
for _ in range(1000):
    signs={c:rng.choice([-1.0,1.0]) for c in clist}
    w=np.array([signs[c] for c in idx_c])
    yb=np.array(m0.fittedvalues)+w*resid
    b3s.append(sm.OLS(yb,X).fit().params[3])
b3s=np.array(b3s); ci=np.percentile(b3s,[2.5,97.5])
print(f"  2020-2025 β3={b3_hat:+.3f}, 95% wild-CI [{ci[0]:+.3f},{ci[1]:+.3f}], p={float((np.sum(np.abs(b3s)>=abs(b3_hat))+1)/(1000+1)):.3f}")

# 2020-2024 子集 bootstrap
Qd2=within([r["unemp"] for r in sub24],[r["code"] for r in sub24],[r["year"] for r in sub24])
Id2=within([r["iaci"] for r in sub24],[r["code"] for r in sub24],[r["year"] for r in sub24])
Ad2=within([r["imp"] for r in sub24],[r["code"] for r in sub24],[r["year"] for r in sub24])
Gd2=within([r["gdp"] for r in sub24],[r["code"] for r in sub24],[r["year"] for r in sub24])
Ud2=within([r["urban"] for r in sub24],[r["code"] for r in sub24],[r["year"] for r in sub24])
zQ2,zI2,zA2=zs(Qd2),zs(Id2),zs(Ad2); zIA2=zs(np.array(Id2)*np.array(Ad2)); zG2,zU2=zs(Gd2),zs(Ud2)
X2=sm.add_constant(np.column_stack([zI2,zA2,zIA2,zG2,zU2]))
m02=sm.OLS(zQ2,X2).fit(); resid2=np.array(m02.resid); b3_24=m02.params[3]
ic24=[r["code"] for r in sub24]; clist24=sorted(set(ic24)); b3s24=[]
for _ in range(1000):
    signs={c:rng.choice([-1.0,1.0]) for c in clist24}
    w=np.array([signs[c] for c in ic24])
    yb=np.array(m02.fittedvalues)+w*resid2
    b3s24.append(sm.OLS(yb,X2).fit().params[3])
b3s24=np.array(b3s24); ci24=np.percentile(b3s24,[2.5,97.5])
print(f"  2020-2024 β3={b3_24:+.3f}, 95% wild-CI [{ci24[0]:+.3f},{ci24[1]:+.3f}], p={float((np.sum(np.abs(b3s24)>=abs(b3_24))+1)/(1000+1)):.3f}")

print("\n[注] 论文 Q=负失业率 -> 论文 β3>0 对应本表失业率 β3<0；论文 headline β3=0.054(p=0.0002) 依赖 IFR 授权数据。")
print("DONE")
