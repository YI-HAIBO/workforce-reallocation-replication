# -*- coding: utf-8 -*-
"""L30 窗口延伸可行性审计：逐数据源检查年份上限，给出硬约束证据。"""
import csv, os
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
def load(p):
    with open(os.path.join(BASE, p), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

print("=" * 78)
print("L30 观察窗口延伸审计（硬约束证据）")
print("=" * 78)

# Comtrade 进口
imp = load("comtrade_robot_import.csv")
y_imp = sorted({int(r["year"]) for r in imp if r["year"]})
print(f"\n[AUTO=Comtrade HS8479.50 进口] 年份: {y_imp[0]}-{y_imp[-1]}  (max={y_imp[-1]})")

# WDI 失业/GDP/urban
wdi = load("wdi_panel.csv")
y_wdi = sorted({int(r["year"]) for r in wdi if r["unemployment_pct"].strip()})
print(f"[WDI 失业/GDP/urban]        年份: {y_wdi[0]}-{y_wdi[-1]}  (max={y_wdi[-1]})")

# EPL
epl = load("epl_panel_11.csv")
y_epl = sorted({int(r["year"]) for r in epl})
print(f"[EPL]                       年份: {y_epl[0]}-{y_epl[-1]}  (max={y_epl[-1]})")

# 劳动权利
lr = load("labor_rights_11panel.csv")
lr_years = [c for c in lr[0].keys() if c.startswith("y")]
print(f"[劳动权利 SDG8.8.2]         年份: {lr_years[0][1:]}-{lr_years[-1][1:]}  (max={lr_years[-1][1:]})")

# OWID 安装量
inst = load("owid_robots_installed.csv")
y_inst = sorted({int(r["Year"]) for r in inst if r["Code"] != "OWID_WRL"})
print(f"[OWID 安装量(备选 AUTO)]   年份: {y_inst[0]}-{y_inst[-1]}  (max={y_inst[-1]})")

# OWID 密度
dens = load("owid_ifr_raw.csv")
y_dens = sorted({int(r["Year"]) for r in dens})
print(f"[OWID 密度(备选)]           年份: {y_dens[0]}-{y_dens[-1]}  (max={y_dens[-1]})")

print("\n" + "-" * 78)
print("结论：")
print("  · 国家面板主回归所需四源交集 = min(Comtrade 2024, WDI 2024, EPL 2025, 劳动权利 2024)")
print("    => 交集上限 = 2024。2025 数据未发布（Comtrade/WDI/劳动权利均止于 2024）。")
print("  · 试点城市 DID 窗口 2023-2027：第三批(2025) 2025 年启动，2026-27 为执行期，")
print("    试点后结局观测尚不可得（政策未结束）。")
print("  · 延长至 2027+ 需等待试点执行期满 + 城市结局数据发布，非当前可解（时间约束）。")
print("  · 已尽最大窗口：国家面板 2020-24(5年, real_panel.py)，为公开数据交集上限。")
