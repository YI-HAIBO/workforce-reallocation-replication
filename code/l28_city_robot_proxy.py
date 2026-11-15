# -*- coding: utf-8 -*-
"""L28 城市级机器人密度插补（两级分摊，透明规则）：
Stage 1: 全国机器人密度(2024=166/万人, OWID/IFR) -> 省（按各省制造业就业占比, 七普）
Stage 2: 省 -> 试点城市（按城市常住人口占该省试点城人口份额, 七普 qipu）
局限（如实注明）：仅省级制造业占比部分公开, 省内按人口分摊为代理；
城市级真实安装量未公布（NBS），此表为"设计前提"的量化插补而非实测值。
"""
import csv, json, os, math

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

# ---- 七普 各省制造业就业占比（%），来源：中国人口普查年鉴-2020（第一财经计算）----
# 已知：浙江38.2 广东34.0 江苏29.0 全国18.1；9省高于均值(浙江/广东/江苏/福建/上海/江西/天津/河北/山东)
# 未公布的省用全国均值 18.1 作保守缺省（注明）
PROV_MFG_SHARE = {
    "浙江": 38.2, "广东": 34.0, "江苏": 29.0, "福建": 24.0, "上海": 23.0,
    "江西": 21.0, "天津": 20.0, "河北": 19.0, "山东": 19.0,
}
NATIONAL_MFG_SHARE = 18.1
NATIONAL_ROBOT_DENSITY = 166.0   # 2024, 台/万就业人员（OWID/IFR 2025）

# ---- 七普 各省常住人口（万人，七普公报第二号 2020-11-01）----
# 用于省内分摊分母：城市份额 = 城市常住 / 全省常住（避免"单试点城省份"整省密度伪影）
PROV_TOTAL_POP = {
    "广东": 12601.25, "山东": 10152.75, "河南": 9936.55, "江苏": 8474.80,
    "四川": 8367.49, "河北": 7461.02, "湖南": 6644.49, "浙江": 6456.76,
    "安徽": 6102.72, "湖北": 5775.26, "广西": 5012.68, "云南": 4720.93,
    "江西": 4518.86, "辽宁": 4259.14, "福建": 4154.01, "陕西": 3952.90,
    "贵州": 3856.21, "山西": 3491.56, "重庆": 3205.42, "黑龙江": 3185.01,
    "新疆": 2585.23, "甘肃": 2501.98, "上海": 2487.09, "吉林": 2407.35,
    "内蒙古": 2404.92, "北京": 2189.31, "天津": 1386.60, "海南": 1008.12,
    "宁夏": 720.27, "青海": 592.40,
}

# ---- 加载试点登记与七普 ----
from pilot_registry import PILOTS
qipu = json.load(open(os.path.join(BASE, "qipu_collected.json"), encoding="utf-8"))["city"]

def res_of(name):
    r = qipu.get(name)
    if r is None: return None
    return r.get("res")

# 省内聚合（只对试点城）
prov_pop = {}
for (name, prov, batch, year, admin) in PILOTS:
    r = res_of(name)
    if r:
        prov_pop[prov] = prov_pop.get(prov, 0.0) + r

rows = []
for (name, prov, batch, year, admin) in PILOTS:
    r = res_of(name)
    if not r: continue
    share = PROV_MFG_SHARE.get(prov, NATIONAL_MFG_SHARE)
    # 省密度 = 全国密度 × (省制造业占比/全国占比)
    prov_density = NATIONAL_ROBOT_DENSITY * (share / NATIONAL_MFG_SHARE)
    # 市内份额 = 城市常住(万人) / 全省常住(万人)  —— 用省域总人口做分母
    prov_total = PROV_TOTAL_POP.get(prov)
    if prov_total:
        city_w = (r / 10000.0) / prov_total
    else:
        city_w = r / prov_pop[prov]  # 无省域总数时退回试点城占比（兵团等）
    city_density = prov_density * city_w
    rows.append({
        "城市": name, "省": prov, "批次": batch, "年份": year,
        "常住人口(万)": round(r / 10000.0, 1),
        "省制造业占比%": share, "省密度(台/万)": round(prov_density, 1),
        "城市密度代理(台/万)": round(city_density, 3),
        "省内份额%": round(city_w * 100, 3),
        "备注": "实测省占比" if prov in PROV_MFG_SHARE else "省占比按全国均值缺省",
    })

rows.sort(key=lambda x: -x["城市密度代理(台/万)"])
out = os.path.join(BASE, "L28_city_robot_density_proxy_2024.csv")
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(f"输出 {len(rows)} 城 -> {out}")
print("== 城市密度代理 TOP12 ==")
for r in rows[:12]:
    print(f"  {r['城市']:<10}{r['省']:<4} 批{r['批次']}  代理={r['城市密度代理(台/万)']:>8.3f}  (省占比{ r['省制造业占比%']}%)")
print("== BOTTOM5 ==")
for r in rows[-5:]:
    print(f"  {r['城市']:<10}{r['省']:<4} 批{r['批次']}  代理={r['城市密度代理(台/万)']:>8.3f}")
print(f"\n省内分摊：城市密度均值 = {sum(r['城市密度代理(台/万)'] for r in rows)/len(rows):.3f} 台/万")
print("局限：省内按常住人口占比分摊为代理（城市制造业就业未公布）；此为设计前提量化插补。")
