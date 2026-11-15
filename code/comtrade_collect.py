import urllib.request, ssl, json, time, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

codes = {"Germany":276,"France":250,"Sweden":752,"Italy":380,"Rep. Korea":410,
         "Spain":724,"Japan":392,"China":156,"Brazil":76,"Mexico":484,"United States":842}

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 Chrome/120","Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()

rows = []
log = []
for name, rc in codes.items():
    for yr in range(2020, 2025):
        url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=%d&period=%d&cmdCode=847950&flowCode=M" % (rc, yr)
        ok = False
        for attempt in range(3):
            try:
                d = get(url)
                obj = json.loads(d.decode("utf-8", errors="replace"))
                data = obj.get("data", [])
                val = None
                for r in data:
                    if r.get("flowCode") == "M":
                        val = r.get("primaryValue")
                        break
                rows.append({"country":name,"code":rc,"year":yr,"robot_import_usd":val})
                log.append("%s %d -> %s" % (name, yr, val))
                ok = True
                break
            except Exception as e:
                log.append("%s %d attempt%d ERR %r" % (name, yr, attempt, e))
                time.sleep(5)
        time.sleep(3.5)
        if not ok:
            rows.append({"country":name,"code":rc,"year":yr,"robot_import_usd":None})

import csv
with open(os.path.join(BASE,"comtrade_robot_import.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["country","code","year","robot_import_usd"])
    w.writeheader(); w.writerows(rows)
with open(os.path.join(BASE,"comtrade_log.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(log))
print("DONE rows:", len(rows))
print("\n".join(log[:40]))
