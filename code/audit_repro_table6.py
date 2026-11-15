# -*- coding: utf-8 -*-
"""复现论文表 6 面板回归：在 iaciauto_panel.csv (C 版) 上按论文规格估计 β3。
论文规格：Q=-unemployment; AUTO=IFR 密度; IACI=等权 min-max(0-6) 归一化成分;
双固定效应(国家+年份); 聚类稳健 SE(国家); 11 国 2000-2024。
输出与论文表 6 第(4)列 β3=+0.054*** (p=0.0002) 对比。
"""
import pandas as pd, numpy as np, os
import statsmodels.api as sm

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
p = r"E:\task\论文：Directional Evidence on Workforce Reallocation in China's\2026-10-07_C_version\l2_data\iaciauto_panel.csv"

df = pd.read_csv(p)
# 只留真实国家(11)且 2000-2024
real = ["Canada","China","France","Germany","India","Italy","Japan","Korea","Mexico","UK","US"]
df = df[df["country"].isin(real) & df["year"].between(2000,2024)].copy()
df = df.dropna(subset=["ROB","EPL","WREPL","COD","UNEMP"]).reset_index(drop=True)
print("sample: n=%d, countries=%d, years=%d-%d" % (len(df), df["country"].nunique(), df["year"].min(), df["year"].max()))
print("countries:", sorted(df["country"].unique()))

def mm(s):
    lo, hi = s.min(), s.max()
    return (s-lo)/(hi-lo)*6 if hi > lo else s*0

for c in ["EPL","WREPL","COD"]:
    df[c+"_06"] = mm(df[c].astype(float))
# 等权 3 成分 IACI（robust_panel.py 的论文口径）
df["IACI"] = (df["EPL_06"]+df["WREPL_06"]+df["COD_06"])/3
df["Q"] = -df["UNEMP"].astype(float)
df["AUTO"] = df["ROB"].astype(float)
df["IACIxAUTO"] = df["IACI"]*df["AUTO"]

# 双固定效应 within 变换
def within_dm(data, y, xv, unit, time):
    dd = data.copy()
    for v in [y]+xv:
        dd[v+"_dm"] = dd[v] - dd.groupby(unit)[v].transform("mean")
        dd[v+"_dm"] = dd[v+"_dm"] - dd.groupby(time)[v+"_dm"].transform("mean")
    return dd

cols = ["IACI","AUTO","IACIxAUTO","gdp","urban"] if False else None

# 论文表6 第(4)列: Q ~ IACI + AUTO + IACIxAUTO + GDPpc + Urban, 双FE, 聚类国家
# 但 iaciauto_panel 无 GDPpc/urban -> 先用无控制版 (列2) 和有 IACIxAUTO 版对比
def fe_reg(data, y, xv, unit="country", time="year"):
    dd = within_dm(data, y, xv, unit, time)
    X = sm.add_constant(dd[[v+"_dm" for v in xv]])
    res = sm.OLS(dd[y+"_dm"], X).fit(cov_type="cluster", cov_kwds={"groups": dd[unit]})
    return res, len(dd)

# 列1: 仅 IACI
r1,n1 = fe_reg(df, "Q", ["IACI"])
# 列2: IACI + AUTO
r2,n2 = fe_reg(df, "Q", ["IACI","AUTO"])
# 列4: IACI + AUTO + 交互 (无 GDP/urban，因为面板缺这两列)
r4,n4 = fe_reg(df, "Q", ["IACI","AUTO","IACIxAUTO"])
print("\n--- 复现（无控制，因面板缺 GDP/urban）---")
for name, r, n in [("col1 IACI", r1, n1), ("col2 +AUTO", r2, n2), ("col4 +interaction", r4, n4)]:
    print("  %-16s n=%d" % (name, n))
    for p_ in r.params.index:
        if p_ == "const": continue
        print("    %-14s b=%+8.4f  se=%6.4f  t=%7.3f  p=%.4f" % (p_, r.params[p_], r.bse[p_], r.tvalues[p_], r.pvalues[p_]))

# 论文表6: IACI=-2.823***, AUTO=-0.165***, IACIxAUTO=+0.054***, n=272
print("\n论文表6 第(4)列(含GDP/urban): IACI=-2.823***, AUTO=-0.165***, IACIxAUTO=+0.054***, n=272")
