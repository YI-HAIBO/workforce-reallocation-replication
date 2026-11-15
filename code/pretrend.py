# -*- coding: utf-8 -*-
"""L26/L27 pre-trend 双组对比：政策（T1=2023）前的 2010六普 -> 2020七普 流入趋势。
扩张组 = 浙江(杭州/宁波/温州/金华/绍兴/丽水) + 福建(福州/泉州/漳州)
收缩组 = 东北(沈阳/大连/盘锦/哈尔滨/齐齐哈尔/大庆/长春/吉林市) + 山西(太原/长治/晋中)
判据：扩张组 2010-2020 净流入为正且增长；收缩组为负或近零 -> 支持"扩张驱动"假说
      （L24/L25 可证伪判据的政策前证据）；若两组方向一致 -> 扩张驱动被证伪。
Y = 常住人口（六普2010-11-01 / 七普2020-11-01，同口径普查时点）。"""
import csv, json

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

# 六普 2010 常住（人）——省七普/六普公报地区分布表
RES_2010 = {
    # 浙江（六普公报）
    "杭州": 8700400, "宁波": 7605700, "温州": 9122100,
    "金华": 5361600, "绍兴": 4912200, "丽水": 2117000,
    # 福建（六普公报）
    "福州": 7115370, "泉州": 8128530, "漳州": 4809983,
    # 辽宁（六普公报）
    "沈阳": 8106171, "大连": 6690432, "盘锦": 1392493,
    # 黑龙江（六普公报）
    "哈尔滨": 10635971, "齐齐哈尔": 5367003, "大庆": 2904532,
    # 吉林（六普公报）
    "长春": 7677089, "吉林市": 4414681,
    # 山西（六普公报）
    "太原": 4201591, "长治": 3334564, "晋中": 3249425,
}

EXPAND = ["杭州", "宁波", "温州", "金华", "绍兴", "丽水", "福州", "泉州", "漳州"]
CONTRACT = ["沈阳", "大连", "盘锦", "哈尔滨", "齐齐哈尔", "大庆", "长春", "吉林市", "太原", "长治", "晋中"]

# 七普 2020 常住（人）
qipu = json.load(open(BASE + r"\qipu_collected.json", encoding="utf-8"))["city"]

def seven(city):
    rec = qipu.get(city) or qipu.get(city + "市")
    return rec["res"] if rec and rec.get("res") else None

rows = []
for city in EXPAND + CONTRACT:
    g = "扩张" if city in EXPAND else "收缩"
    r10 = RES_2010[city]
    r20 = seven(city)
    if r20 is None:
        continue
    delta = r20 - r10
    rows.append([city, g, r10, r20, delta, round(delta / r10 * 100, 2)])

with open(BASE + r"\pretrend_2010_2020.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["城市", "组", "常住_六普2010", "常住_七普2020", "变化(万人以下)", "变化%"])
    w.writerows(rows)

# 分组汇总
def agg(cities):
    d = [r[4] for r in rows if r[1] == cities]
    p10 = [r[2] for r in rows if r[1] == cities]
    p20 = [r[3] for r in rows if r[1] == cities]
    return sum(d), sum(p10), sum(p20), (sum(d) / sum(p10) * 100)

de, p10e, p20e, pcte = agg("扩张")
dc, p10c, p20c, pctc = agg("收缩")
print(f"扩张组(n={len(EXPAND)}): 2010={p10e/1e4:.0f}万 -> 2020={p20e/1e4:.0f}万, 净增{de/1e4:.0f}万 ({pcte:+.1f}%)")
print(f"收缩组(n={len(CONTRACT)}): 2010={p10c/1e4:.0f}万 -> 2020={p20c/1e4:.0f}万, 净增{dc/1e4:.0f}万 ({pctc:+.1f}%)")

# 逐城
print("\n逐城变化(2010->2020):")
for r in sorted(rows, key=lambda x: -x[4]):
    print(f"  [{r[1]}] {r[0]}: {r[2]/1e4:.0f} -> {r[3]/1e4:.0f}万 ({r[5]:+.2f}%)")

n_expand_pos = sum(1 for r in rows if r[1] == "扩张" and r[4] > 0)
n_contract_neg = sum(1 for r in rows if r[1] == "收缩" and r[4] < 0)
print(f"\n扩张组净流入>0: {n_expand_pos}/{len(EXPAND)}; 收缩组净流入<0: {n_contract_neg}/{len(CONTRACT)}")
