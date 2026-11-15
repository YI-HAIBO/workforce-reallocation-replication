# -*- coding: utf-8 -*-
"""L31 就绪：Callaway-Sant'Anna 组时 ATT 聚合 + pre-trend/安慰剂/预期检验（§5.3 识别设计）。
数据到位后运行：city_panel.csv [city, year, G, Y, X...]（G=首次处理年, 0=从未处理）。
依赖：pandas, numpy；可选 csdid/DRDID（IPW/双重稳健）。
"""
import pandas as pd
import numpy as np

# ---------------- 配置 ----------------
PANEL = "city_panel.csv"      # 城市×年份面板
Y = "Q"                       # 结果：再配置强度 Q
G = "G"                       # 首次处理年份（0=从未处理）
UNIT = "city"
TIME = "year"
COVARS = ["robot_city", "gdp_pcap", "urban", "mfg_share"]  # 城市级协变量（L28 需年鉴汇编/插补）
ANTICIPATION = 1              # 预期窗口（L27）

# ---------------- 数据加载 ----------------
df = pd.read_csv(PANEL)
df[G] = df[G].fillna(0).astype(int)
never = df[df[G] == 0].copy()

# ---------------- 最小 C-SA 组时 ATT（语义与 csdid 一致） ----------------
def group_time_att(df, never, g, t, base):
    """ATT(g,t) = E[Y_t-Y_{g-1}|G=g] - E[Y_t-Y_{g-1}|G=0]"""
    dg = df[(df[G] == g) & (df[TIME] == t)][Y].mean() - df[(df[G] == g) & (df[TIME] == base)][Y].mean()
    dn = never[never[TIME] == t][Y].mean() - never[never[TIME] == base][Y].mean()
    return dg - dn

rows = []
for g in sorted(df[df[G] > 0][G].unique()):
    base = g - 1
    for t in sorted(df[TIME].unique()):
        if t < base:            # 只保留 base 及之后
            continue
        att = group_time_att(df, never, g, t, base)
        rows.append({"g": g, "t": t, "e": t - g, "att": att})
r = pd.DataFrame(rows)

# ---------------- 聚合 ----------------
att_event = r.groupby("e")["att"].mean()     # 事件时间聚合（L31 一级报告）
att_group = r.groupby("g")["att"].mean()     # 组别聚合
simple = r["att"].mean()                     # 简单聚合
print("== 事件时间聚合 ATT(e) ==")
print(att_event.round(4))
print("== 组别聚合 ATT(g) ==")
print(att_group.round(4))
print(f"简单聚合 = {simple:.4f}")

# ---------------- L25/L27：pre-trend 安慰剂 + 预期检验 ----------------
pre = att_event[[e for e in att_event.index if e < 0]]
print("\n== pre-trend 系数 ATT(e<0)（应接近 0）==")
print(pre.round(4))
print(f"max|pre| = {abs(pre).max():.4f}")

# L27 预期：t=g-1 先行反应
antic = r[r["e"] == -1]
print(f"\n== 预期检验 ATT(e=-1) = {antic['att'].mean():.4f}（≈0 → 无预期效应）==")

# ---------------- L27 安慰剂：处理时点前移 1-2 年 ----------------
df_p = df.copy()
df_p.loc[df_p[G] > 0, G] = df_p.loc[df_p[G] > 0, G] - 1   # placebo g' = g-1
rows_p = []
for g in sorted(df_p[df_p[G] > 0][G].unique()):
    base = g - 1
    for t in sorted(df_p[TIME].unique()):
        if t < base: continue
        att = group_time_att(df_p, never, g, t, base)
        rows_p.append({"g": g, "t": t, "e": t - g, "att": att})
rp = pd.DataFrame(rows_p)
placebo_pre = rp[rp["e"] < 0].groupby("e")["att"].mean()
print("\n== 安慰剂（处理前移 1 年）pre 系数 ATT(e<0)（应≈0）==")
print(placebo_pre.round(4))

# ---------------- L30：窗口扩展（若数据含 2028+ 则自动纳入） ----------------
print(f"\n== 窗口：{df[TIME].min()}-{df[TIME].max()}（延长至 2028+ 需数据到位）==")

# ---------------- 正式估计建议 ----------------
print("\n[正式估计] 建议用 csdid(R)/DRDID(Python) 实现 IPW/双重稳健，聚类到城市，bootstrap 推断；")
print("          本骨架用从未处理为对照、基期 g-1、事件时间 e=t-g，语义与 C-SA 一致。")
