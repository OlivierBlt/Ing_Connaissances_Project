import json
import urllib.request

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZmIyMGVmMmRlMDlmZjkwZDZhYzc0MjcyYWQ1ZjYyMCIsIm5iZiI6MTc5NDgyMzcxNS4wMjEsInN1YiI6IjZhZmFkNjIzMzRlNDkzNjZmMzZkMDNkOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.I6cX3FgTZmEsLMIF-iCJzy_CkEnJ5XFHzAzoF76a8Vo"
API = "https://api.themoviedb.org/3"


MOVIE = ["id", "title", "original_title", "original_language", "release_date", "runtime", "status",
         "overview", "tagline", "vote_average", "vote_count", "popularity", "budget", "revenue"]
TV = ["id", "name", "original_name", "original_language", "origin_country", "first_air_date", "last_air_date",
      "status", "number_of_seasons", "number_of_episodes", "overview", "vote_average", "vote_count", "popularity"]


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


def pick(d, keys):
    return {k: d.get(k) for k in keys}


def names(items):
    return [x["name"] for x in items]


def movie(d):
    coll = d["belongs_to_collection"]
    return pick(d, MOVIE) | {
        "genres": [pick(g, ["id", "name"]) for g in d["genres"]],
        "belongs_to_collection": pick(coll, ["id", "name"]) if coll else None,
        "credits": {
            "cast": [pick(c, ["name", "character", "order"]) for c in d["credits"]["cast"]],
            "crew": [pick(c, ["name", "job"]) for c in d["credits"]["crew"]],
        },
        "keywords": {"keywords": [pick(k, ["id", "name"]) for k in d["keywords"]["keywords"]]},
        "production_companies": names(d["production_companies"]),
        "production_countries": names(d["production_countries"]),
        "external_ids": pick(d["external_ids"], ["imdb_id", "wikidata_id"]),
    }


def tv(d):
    return pick(d, TV) | {
        "genres": [pick(g, ["id", "name"]) for g in d["genres"]],
        "created_by": names(d["created_by"]),
        "networks": names(d["networks"]),
        "aggregate_credits": {
            "cast": [{"name": c["name"], "roles": [pick(r, ["character"]) for r in c["roles"]], "order": c["order"]}
                     for c in d["aggregate_credits"]["cast"]],
        },
        "keywords": {"results": [pick(k, ["id", "name"]) for k in d["keywords"]["results"]]},
        "external_ids": pick(d["external_ids"], ["imdb_id", "wikidata_id"]),
    }


def save(name, data):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


for kind, credits, clean in [("movie", "credits", movie), ("tv", "aggregate_credits", tv)]:
    save(f"genres_{kind}.json", get(f"/genre/{kind}/list"))
    popular = discover(kind, 50, sort_by="popularity.desc", **{"vote_count.gte": 200})
    adaptations = discover(kind, 500, with_keywords=41645)
    ids = list(dict.fromkeys(popular + adaptations))
    print(kind, len(ids))
    items = [clean(get(f"/{kind}/{i}", append_to_response=f"{credits},keywords,external_ids")) for i in ids]
    save(f"{kind}.json", items)
