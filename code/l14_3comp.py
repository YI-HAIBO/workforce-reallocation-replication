# -*- coding: utf-8 -*-
"""L14 攻坚：三成分观测 IACI（EPL + 劳动权利 + ALMP/LMPs 支出）替代文献校准子成分。
新增第三子成分：真实 OECD ALMP/LMPs 支出（%GDP，公开检索值）。
样本 = EPL+LR+IFR24+WDI 齐全 且 有 LMPs 值 的 OECD 子样本。"""
import csv, os, math
import numpy as np
import statsmodels.api as sm

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

def load_rows(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

epl = {r["iso3"].strip(): float(r["ept"]) for r in load_rows(os.path.join(BASE, "epl_panel_11.csv")) if r["iso3"].strip()}
lr  = {r["code"].strip(): float(r["y2024"]) for r in load_rows(os.path.join(BASE, "labor_rights_11panel.csv")) if r["code"].strip()}
ifr = {r["code"].strip(): (float(r["density_2024"]) if r.get("density_2024") else None)
       for r in load_rows(os.path.join(BASE, "ifr_density_2023_2024.csv")) if r["code"].strip()}
wdi = {}
for r in load_rows(os.path.join(BASE, "wdi_panel.csv")):
    try: y = int(r["year"])
    except Exception: continue
    wdi[(r["country_code"].strip(), y)] = r

NAME = {"DEU":"Germany","FRA":"France","SWE":"Sweden","ITA":"Italy","KOR":"Rep. Korea",
        "ESP":"Spain","JPN":"Japan","MEX":"Mexico","USA":"United States"}

# 真实 ALMP 支出（%GDP）：OECD Strengthening ALMPs in Korea (2024) via datawrapper；
# 总 LMPs 2023（含被动）：Eurostat lmp_expsumm 镜像。ALMP 更贴近论文"工资替代/培训"子成分，取 ALMP 列。
ALMP = {"SWE":1.3, "FRA":1.0, "DEU":0.7, "KOR":0.6, "USA":0.1}  # 2024（JPN/MEX 无公开值）
LMP_TOT = {"ESP":2.38, "FRA":2.49, "ITA":1.56, "DEU":1.42, "SWE":1.28, "KOR":0.6, "USA":0.1}  # 2023 总口径

rows = []
for c in ["DEU","FRA","SWE","ITA","KOR","ESP","JPN","MEX","USA"]:
    if c not in epl or c not in lr: continue
    d24 = ifr.get(c)
    gdp = unemp = urban = None
    for y in (2024, 2023):
        if (c, y) in wdi:
            w = wdi[(c, y)]
            gdp = float(w["gdp_pcap_usd"]); unemp = float(w["unemployment_pct"]); urban = float(w["urban_pct"]); break
    lmp = LMP_TOT.get(c)
    if lmp is None: continue
    rows.append(dict(code=c, name=NAME[c], ept=epl[c], lr=lr[c], ifr=d24,
                     gdp=gdp, unemp=unemp, urban=urban, lmp=lmp,
                     almp=ALMP.get(c)))

reg = [r for r in rows if r["ifr"] is not None and r["gdp"] is not None and r["unemp"] is not None]
print(f"三成分样本（EPL+LR+LMPs+IFR24+WDI 齐全）：{len(reg)} 国 -> {[r['name'] for r in reg]}")

def normv(vals):
    lo, hi = min(vals), max(vals)
    return [(v-lo)/(hi-lo) for v in vals]

e_n = normv([r["ept"] for r in reg])
l_n = normv([r["lr"] for r in reg])
p_n = normv([r["lmp"] for r in reg])

def xs(iaci, auto, y):
    m = sm.OLS(np.array(y), sm.add_constant(np.column_stack([np.array(iaci), np.array(auto),
             np.array(iaci)*np.array(auto)]))).fit()
    return m.params[3], m.pvalues[3]

q = [r["unemp"] for r in reg]          # 失业率（论文 Q=非失业，符号取反即同口径）
a = [r["ifr"] for r in reg]

iaci2 = [(e_n[i]+l_n[i])/2*6 for i in range(len(reg))]
iaci3 = [(e_n[i]+l_n[i]+p_n[i])/3*6 for i in range(len(reg))]

b3_2, p_2 = xs(iaci2, a, q)
b3_3, p_3 = xs(iaci3, a, q)
print(f"2成分 IACI(等权EPL+LR):   b3(失业口径)={b3_2:+.3f}  p={p_2:.3f}")
print(f"3成分 IACI(等权+LMPs):    b3(失业口径)={b3_3:+.3f}  p={p_3:.3f}")
print(f"-> 论文 Q 口径：2成分 {b3_2:+.3f} / 3成分 {b3_3:+.3f}（取反）")
print("\n3成分 IACI 排名（0-6）:")
for r, v in sorted(zip(reg, iaci3), key=lambda x: -x[1]):
    print(f"  {r['name']:<12} IACI3={v:5.2f}  (EPL={r['ept']:.2f}, LR={r['lr']:.2f}, LMPs={r['lmp']:.2f}%)")
print("\n注意：n=%d 为描述性截面，非论文 11 国面板；L14 完整时变 3 成分面板需 OECD LMPs 逐年 API（沙箱 502），单年第三子成分已可观测化。" % len(reg))
