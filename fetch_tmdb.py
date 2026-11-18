import json
import urllib.request

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZmIyMGVmMmRlMDlmZjkwZDZhYzc0MjcyYWQ1ZjYyMCIsIm5iZiI6MTc5NDgyMzcxNS4wMjEsInN1YiI6IjZhZmFkNjIzMzRlNDkzNjZmMzZkMDNkOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.I6cX3FgTZmEsLMIF-iCJzy_CkEnJ5XFHzAzoF76a8Vo"
API = "https://api.themoviedb.org/3"


def get(path, **params):
    params["language"] = "en-US"
    query = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(f"{API}{path}?{query}", headers={"Authorization": f"Bearer {TOKEN}"})
    return json.load(urllib.request.urlopen(req))


def discover(kind, max_pages, **filters):
    ids = []
    for page in range(1, max_pages + 1):
        data = get(f"/discover/{kind}", page=page, **filters)
        ids += [r["id"] for r in data["results"]]
        if page >= data["total_pages"]:
            break
    return ids


def save(name, data):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


for kind, credits in [("movie", "credits"), ("tv", "aggregate_credits")]:
    save(f"genres_{kind}.json", get(f"/genre/{kind}/list"))
    popular = discover(kind, 50, sort_by="popularity.desc", **{"vote_count.gte": 200})
    adaptations = discover(kind, 500, with_keywords=41645)
    ids = list(dict.fromkeys(popular + adaptations))
    print(kind, len(ids))
    items = [get(f"/{kind}/{i}", append_to_response=f"{credits},keywords,external_ids") for i in ids]
    save(f"{kind}.json", items)