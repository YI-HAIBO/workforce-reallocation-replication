import urllib.request, ssl, time, os, csv

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
BASE = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08"

countries = {
    "Germany": ["germany"],
    "France": ["france"],
    "Sweden": ["sweden"],
    "Italy": ["italy"],
    "Rep. Korea": ["korea", "republic-of-korea", "south-korea"],
    "Spain": ["spain"],
    "Japan": ["japan"],
    "China": ["china"],
    "Brazil": ["brazil"],
    "Mexico": ["mexico"],
    "United States": ["united-states", "usa", "united-states-of-america"],
}

def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Chrome/120"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()

slug_tests = ["strictness-of-employment-protection-temporary-contracts",
              "strictness-of-employment-protection-regular-contracts",
              "strictness-of-employment-protection"]

# 1) Test which EPL indicator slugs exist (on Germany)
print("=== slug availability test (Germany) ===", flush=True)
for slug in slug_tests:
    url = "https://labour.statizoid.com/stat/%s/germany.csv" % slug
    try:
        d = fetch(url)
        print("%s -> OK bytes=%d" % (slug, len(d)), flush=True)
    except Exception as e:
        print("%s -> ERR %r" % (slug, e), flush=True)

# 2) Batch download EPT (temporary) for 11 countries
print("=== batch EPT download ===", flush=True)
results = []
for name, slugs in countries.items():
    ok = False
    for slug in slugs:
        url = "https://labour.statizoid.com/stat/strictness-of-employment-protection-temporary-contracts/%s.csv" % slug
        try:
            d = fetch(url)
            fname = os.path.join(BASE, "ept_%s.csv" % name.replace(".", "").replace(" ", "_"))
            with open(fname, "wb") as f:
                f.write(d)
            lines = d.decode("utf-8", errors="replace").splitlines()
            results.append("%s OK slug=%s rows=%d (%s)" % (name, slug, len(lines)-1, fname))
            ok = True
            break
        except Exception as e:
            pass
    if not ok:
        results.append("%s FAIL (all slugs)" % name)
    time.sleep(0.5)

with open(os.path.join(BASE, "ept_download_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(results))
print("\n".join(results), flush=True)
