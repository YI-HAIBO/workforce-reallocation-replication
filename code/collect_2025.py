# -*- coding: utf-8 -*-
"""L30 替代方案 A1：采集 Comtrade 2025 + WDI 2025 全 11 国，追加到现有 CSV。
为 EPL 单成分 IACI 的 2020-2025 六年面板提供数据基础。"""
import urllib.request, ssl, json, csv, os, time, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

def get(url, timeout=45, headers=None):
    h = {"User-Agent": "Mozilla/5.0 Chrome/120", "Accept": "*/*"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()

def log(s):
    sys.stdout.write(s + "\n"); sys.stdout.flush()

# 国家码映射
CODES = {"Germany":276,"France":250,"Sweden":752,"Italy":380,"Rep. Korea":410,
         "Spain":724,"Japan":392,"China":156,"Brazil":76,"Mexico":484,"United States":842}
CODE3 = {"276":"DEU","250":"FRA","752":"SWE","380":"ITA","410":"KOR","724":"ESP",
         "392":"JPN","156":"CHN","76":"BRA","484":"MEX","842":"USA"}

print("=" * 74)
print("采集 2025 数据（Comtrade 进口 + WDI 三指标），11 国")
print("=" * 74)

# ---------- 1. Comtrade 2025 ----------
print("\n[1] Comtrade HS8479.50 进口 2025")
imp_2025 = {}
for name, rc in CODES.items():
    url = f"https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode={rc}&period=2025&cmdCode=847950&flowCode=M"
    val = None
    for attempt in range(3):
        try:
            d = json.loads(get(url, timeout=50).decode("utf-8", errors="replace"))
            for r in d.get("data", []):
                if r.get("flowCode") == "M":
                    val = r.get("primaryValue"); break
            break
        except Exception as e:
            if attempt == 2:
                log(f"  {name:<14} ERR {e!r}")
            else:
                time.sleep(3)
    imp_2025[CODE3[str(rc)]] = val
    log(f"  {name:<14} 2025 -> {val}")
    time.sleep(2)

# ---------- 2. WDI 2025 ----------
print("\n[2] World Bank WDI 2025")
WDI_COUNTRIES = [("DEU","Germany"),("FRA","France"),("SWE","Sweden"),("ITA","Italy"),
                 ("KOR","Rep. Korea"),("ESP","Spain"),("JPN","Japan"),("CHN","China"),
                 ("BRA","Brazil"),("MEX","Mexico"),("USA","United States")]
INDICATORS = [("SL.UEM.TOTL.ZS","unemployment_pct"),
              ("NY.GDP.PCAP.CD","gdp_pcap_usd"),
              ("SP.URB.TOTL.IN.ZS","urban_pct")]
wdi_2025 = {}
for ccode, cname in WDI_COUNTRIES:
    series = {}
    for icode, iname in INDICATORS:
        url = f"https://api.worldbank.org/v2/country/{ccode}/indicator/{icode}?date=2025&format=json&per_page=5"
        val = None
        for attempt in range(3):
            try:
                d = json.loads(get(url, timeout=40).decode("utf-8"))
                if isinstance(d, list) and len(d) > 1 and isinstance(d[1], list):
                    for row in d[1]:
                        if row.get("value") is not None:
                            val = row["value"]; break
                break
            except Exception as e:
                if attempt == 2:
                    log(f"  {cname:<14} {iname} ERR {e!r}")
                else:
                    time.sleep(2)
        series[iname] = val
        time.sleep(0.4)
    wdi_2025[ccode] = series
    log(f"  {cname:<14} unemp={series['unemployment_pct']} gdp={series['gdp_pcap_usd']} urban={series['urban_pct']}")

# ---------- 3. 追加到现有 CSV ----------
print("\n[3] 追加到现有 CSV")

# Comtrade
imp_path = os.path.join(BASE, "comtrade_robot_import.csv")
imp_rows = []
with open(imp_path, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if int(r["year"]) != 2025:
            imp_rows.append(r)
for c3, val in imp_2025.items():
    if val is not None:
        name_map = {v:k for k,v in CODE3.items()}
        imp_rows.append({"country": {v:k for k,v in CODES.items()}[int(name_map[c3])],
                         "code": name_map[c3], "year": "2025", "robot_import_usd": str(val)})
with open(imp_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["country","code","year","robot_import_usd"])
    w.writeheader(); w.writerows(imp_rows)
n25 = sum(1 for r in imp_rows if r["year"]=="2025")
log(f"  comtrade_robot_import.csv: +{n25} 行 2025 (总计 {len(imp_rows)} 行)")

# WDI
wdi_path = os.path.join(BASE, "wdi_panel.csv")
wdi_rows = []
with open(wdi_path, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if int(r["year"]) != 2025:
            wdi_rows.append(r)
for ccode, cname in WDI_COUNTRIES:
    s = wdi_2025[ccode]
    wdi_rows.append({"country_code": ccode, "country": cname, "year": "2025",
                     "unemployment_pct": s["unemployment_pct"],
                     "gdp_pcap_usd": s["gdp_pcap_usd"],
                     "urban_pct": s["urban_pct"]})
with open(wdi_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["country_code","country","year","unemployment_pct","gdp_pcap_usd","urban_pct"])
    w.writeheader(); w.writerows(wdi_rows)
n25w = sum(1 for r in wdi_rows if r["year"]=="2025")
log(f"  wdi_panel.csv: +{n25w} 行 2025 (总计 {len(wdi_rows)} 行)")

print("\nDONE")