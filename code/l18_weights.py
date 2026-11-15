# -*- coding: utf-8 -*-
"""L18 完整权重矩阵：2020-24 真实面板（7国×5年）交互 β3 在不同 IACI 权重方案下的稳健性。
方案：等权 / 留一(仅EPL) / 留一(仅劳动权利) / PCA / 收入加权。
"""
import csv, os, numpy as np, statsmodels.api as sm

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
def load_rows(p):
    with open(p, encoding="utf-8-sig") as f: return list(csv.DictReader(f))

imp={}
for r in load_rows(os.path.join(BASE,"comtrade_robot_import.csv")):
    try: imp[(r["code"].strip(),int(r["year"]))]=float(r["robot_import_usd"])
    except Exception: pass
epl={}
for r in load_rows(os.path.join(BASE,"epl_panel_11.csv")):
    try: epl[(r["iso3"].strip(),int(r["year"]))]=float(r["ept"])
    except Exception: pass
lr={}
for r in load_rows(os.path.join(BASE,"labor_rights_11panel.csv")):
    c=r["code"].strip()
    for y in range(2015,2025):
        try: lr[(c,y)]=float(r[f"y{y}"])
        except Exception: pass
wdi={}
for r in load_rows(os.path.join(BASE,"wdi_panel.csv")):
    try: wdi[(r["country_code"].strip(),int(r["year"]))]=r
    except Exception: pass
CODE3={"276":"DEU","752":"SWE","380":"ITA","410":"KOR","724":"ESP","392":"JPN","156":"CHN","76":"BRA","484":"MEX","842":"USA"}
NAME={"276":"Germany","752":"Sweden","380":"Italy","410":"Korea","724":"Spain","392":"Japan","156":"China","76":"Brazil","484":"Mexico","842":"US"}

rows=[]
for (c,y) in sorted(imp.keys()):
    c3=CODE3.get(c)
    if not c3 or (c3,y) not in epl or (c3,y) not in lr or (c3,y) not in wdi: continue
    w=wdi[(c3,y)]
    try: rows.append({"code":c3,"year":y,"imp":imp[(c,y)],"ept":epl[(c3,y)],"lr":lr[(c3,y)],
                      "unemp":float(w["unemployment_pct"]),"gdp":float(w["gdp_pcap_usd"]),"urban":float(w["urban_pct"])})
    except Exception: pass
print(f"面板：{len(rows)} 行 = {len(set(r['code'] for r in rows))} 国 × {len(set(r['year'] for r in rows))} 年")

idx_c=[r["code"] for r in rows]; idx_y=[r["year"] for r in rows]
def zs(v):
    v=np.array(v,float); s=v.std(); return (v-v.mean())/s if s>0 else v
def within(v, ic, iy):
    v=np.array(v,float)
    for c in set(ic):
        m=[i for i,x in enumerate(ic) if x==c]; v[m]-=np.mean(v[m])
    for y in set(iy):
        m=[i for i,x in enumerate(iy) if x==y]; v[m]-=np.mean(v[m])
    return v

def norm_panel(vals):
    v=np.array(vals,float); return (v-v.min())/(v.max()-v.min())

E=np.array([r["ept"] for r in rows]); L=np.array([r["lr"] for r in rows]); GDP=np.array([r["gdp"] for r in rows])
En=norm_panel(E); Ln=norm_panel(L)
# 收入加权：以人均 GDP 为权重（高收入国权重更高）——用 GDP 归一化权重
Gw=GDP/GDP.sum()

def iaci_scheme(name):
    if name=="等权": return (En+Ln)/2*6
    if name=="仅EPL": return En*6
    if name=="仅劳动权利": return Ln*6
    if name=="收入加权": return (Gw*En + Gw*Ln)/Gw.sum()*6   # GDP 加权平均
    if name=="PCA":
        Z=np.column_stack([(E-E.mean())/E.std(),(L-L.mean())/L.std()])
        ev,evec=np.linalg.eigh(np.cov(Z.T)); pc=evec[:,np.argmax(ev)]
        z=Z@pc; return (z-z.min())/(z.max()-z.min())*6
    raise ValueError(name)

print("\nL18: 权重矩阵 —— 2020-24 面板双固定效应交互 β3（Q=失业率；论文 Q 口径相反）")
print(f"{'权重方案':<12}{'β3(失业率)':<14}{'p':<8}{'论文Q口径β3':<14}")
for name in ["等权","仅EPL","仅劳动权利","PCA","收入加权"]:
    I=iaci_scheme(name)
    Qd=within([r["unemp"] for r in rows],idx_c,idx_y); Id=within(I,idx_c,idx_y); Ad=within([r["imp"] for r in rows],idx_c,idx_y)
    Gd=within([r["gdp"] for r in rows],idx_c,idx_y); Ud=within([r["urban"] for r in rows],idx_c,idx_y)
    X=sm.add_constant(np.column_stack([zs(Id),zs(Ad),zs(np.array(Id)*np.array(Ad)),zs(Gd),zs(Ud)]))
    m=sm.OLS(zs(Qd),X).fit()
    print(f"{name:<12}{m.params[3]:+.3f}        {m.pvalues[3]:.3f}     {(-m.params[3]):+.3f}")
print("  解读: 论文 Q=负失业率 -> 论文 β3 对应上表'论文Q口径β3'。各权重方案符号一致性见结果。")
print("DONE")
