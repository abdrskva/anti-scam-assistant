from urllib.parse import urlparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Anti-Scam API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BRANDS = ["cdek", "lalafo", "mbank", "optima", "kyrgyzpost", "pochta"]
BAD_TLDS = {".xyz", ".top", ".click", ".site", ".online", ".icu"}
KEYWORDS = ["safe-deal", "bezopasnaya", "delivery", "pay", "secure", "dostavka"]
BLACKLIST = {"cdek-pay.xyz"}  # потом уйдет в БД

def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

class CheckRequest(BaseModel):
    url: str

@app.post("/check")
def check(req: CheckRequest):
    host = (urlparse(req.url).hostname or "").lower()
    score, reasons = 0, []

    if host in BLACKLIST:
        return {"host": host, "score": 100, "reasons": ["Домен в чёрном списке"]}
    if host.startswith("xn--") or "xn--" in host:
        score += 30; reasons.append("Punycode (возможна подмена символов)")
    if any(host.endswith(t) for t in BAD_TLDS):
        score += 20; reasons.append("Подозрительная доменная зона")

    label = host.split(".")[0] if host else ""
    for brand in BRANDS:
        if brand in host and not host.endswith(f"{brand}.ru") and not host.endswith(f"{brand}.kg"):
            score += 40; reasons.append(f"Содержит бренд «{brand}» на чужом домене")
        elif 0 < levenshtein(label, brand) <= 2:
            score += 40; reasons.append(f"Похоже на «{brand}» (тайпсквоттинг)")
    if any(k in host for k in KEYWORDS):
        score += 15; reasons.append("Ключевые слова из схем обмана")
    if host.count("-") >= 2:
        score += 10; reasons.append("Много дефисов в домене")

    return {"host": host, "score": min(score, 100), "reasons": reasons}