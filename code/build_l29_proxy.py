# -*- coding: utf-8 -*-
"""L29 城市级农民工构成代理表：常住(七普) - 户籍(2020年末) = 净流入代理。
按批次输出 CSV + 摘要，供 §5.3 C-SA 设计使用。"""
import json, csv
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
d = json.load(open(BASE + r"\qipu_collected.json", encoding="utf-8"))
c = d["city"]

rows = []
for name, r in c.items():
    res, hko = r.get("res"), r.get("hukou")
    if res is None:
        rows.append([name, r["prov"], r.get("batch"), r.get("year"), "", "", "", "unavailable(兵团)"])
        continue
    if hko is None:
        rows.append([name, r["prov"], r.get("batch"), r.get("year"), res, "", "", "hukou缺失(仅常住)"])
        continue
    net = res - hko
    flag = r.get("flag", "")
    rows.append([name, r["prov"], r.get("batch"), r.get("year"), res, hko, net, flag])

# 按批次/省份排序
rows.sort(key=lambda x: (x[2], x[1], x[0]))
out = BASE + r"\L29_city_proxy_2020.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["城市", "省", "批次", "批次年", "常住_七普2020", "户籍_2020年末", "净流入代理(常住-户籍)", "备注"])
    w.writerows(rows)

# 摘要
n_ok = sum(1 for r in rows if len(r) == 8 and r[6] != "" and "unavailable" not in r[7] and "hukou缺失" not in r[7])
n_res = sum(1 for r in rows if "hukou缺失" in r[7])
n_na = sum(1 for r in rows if "unavailable" in r[7])
n_pos = sum(1 for r in rows if isinstance(r[6], int) and r[6] > 0)
n_neg = sum(1 for r in rows if isinstance(r[6], int) and r[6] < 0)
print(f"total={len(rows)} full双列={n_ok} 仅常住={n_res} 不可得={n_na} 净流入>0={n_pos} <0={n_neg}")
print("TOP10 净流入(农民工流入最强):")
full = [r for r in rows if isinstance(r[6], int)]
for r in sorted(full, key=lambda x: -x[6])[:10]:
    print(f"  {r[0]}({r[1]} B{r[2]}): 净{r[6]/10000:.0f}万  户籍占比{r[5]/r[4]*100:.0f}%")
print("TOP10 净流出(农民工流出):")
for r in sorted(full, key=lambda x: x[6])[:10]:
    print(f"  {r[0]}({r[1]} B{r[2]}): 净{r[6]/10000:.0f}万")
