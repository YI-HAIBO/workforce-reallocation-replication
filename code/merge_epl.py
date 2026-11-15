import csv, os, glob

BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"
out_path = os.path.join(BASE, "epl_panel_11.csv")

rows = []
per = {}
for path in sorted(glob.glob(os.path.join(BASE, "ept_*.csv"))):
    name = os.path.basename(path)
    with open(path, encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                yr = int(row["year"]); val = float(row["value"])
            except Exception:
                continue
            iso = row["iso3"].strip()
            ent = row["entity"].strip()
            rows.append({"country": ent, "iso3": iso, "year": yr, "ept": val})
            per.setdefault(ent, set()).add(yr)

rows.sort(key=lambda x: (x["country"], x["year"]))
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["country", "iso3", "year", "ept"])
    w.writeheader()
    w.writerows(rows)

print("total rows:", len(rows))
for ent in sorted(per):
    ys = sorted(per[ent])
    print("%-16s n=%2d range=%s-%s" % (ent, len(ys), ys[0], ys[-1]))
print("WROTE", out_path)
