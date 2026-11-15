# -*- coding: utf-8 -*-
"""采集 World Bank WDI：失业率(结果Q)、人均GDP、城市化率(控制X)，11 国 2000-2024。"""
import urllib.request, json, ssl, csv, io, os, time

COUNTRIES = [("DEU","Germany"),("FRA","France"),("SWE","Sweden"),("ITA","Italy"),
             ("KOR","Rep. Korea"),("ESP","Spain"),("JPN","Japan"),("CHN","China"),
             ("BRA","Brazil"),("MEX","Mexico"),("USA","United States")]
INDICATORS = [("SL.UEM.TOTL.ZS","unemployment_pct"),
              ("NY.GDP.PCAP.CD","gdp_pcap_usd"),
              ("SP.URB.TOTL.IN.ZS","urban_pct")]
ctx = ssl.create_default_context()

def fetch(code, ind, y0=2000, y1=2024):
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/{ind}?date={y0}:{y1}&format=json&per_page=100"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                out = {}
                for row in data[1]:
                    if row.get("value") is not None:
                        out[int(row["date"])] = row["value"]
                return out
            return {}
        except Exception as e:
            if attempt == 2:
                print("  fetch fail", code, ind, e)
                return {}
            time.sleep(2)

records = []
for ccode, cname in COUNTRIES:
    series = {}
    for icode, iname in INDICATORS:
        series[iname] = fetch(ccode, icode)
        print(f"{cname} {iname}: {len(series[iname])} years")
    for y in range(2000, 2025):
        rec = {"country_code": ccode, "country": cname, "year": y,
               "unemployment_pct": series["unemployment_pct"].get(y),
               "gdp_pcap_usd": series["gdp_pcap_usd"].get(y),
               "urban_pct": series["urban_pct"].get(y)}
        records.append(rec)

out = os.path.join(r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08", "wdi_panel.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["country_code","country","year","unemployment_pct","gdp_pcap_usd","urban_pct"])
    w.writeheader()
    w.writerows(records)

nonmiss = sum(1 for r in records if r["unemployment_pct"] is not None and r["gdp_pcap_usd"] is not None and r["urban_pct"] is not None)
print("rows:", len(records), "complete rows:", nonmiss, "-> saved", out)
