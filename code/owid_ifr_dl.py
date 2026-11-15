import urllib.request, sys

url = "https://ourworldindata.org/grapher/industrial-robots-in-operation-per-1000-employees.csv?v=1&csvType=full&useColumnShortNames=false"
out = r"C:\Users\Yi\WorkBuddy\2026-11-12-17-50-08\owid_ifr_raw.csv"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/csv,*/*",
})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(out, "wb") as f:
        f.write(data)
    print("OK bytes:", len(data))
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    print("lines:", len(lines))
    print("HEADER:", lines[0])
    for ln in lines[1:4]:
        print("ROW:", ln)
except Exception as e:
    print("ERR:", repr(e))
