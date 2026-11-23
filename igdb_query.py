"""Interroge IGDB et enregistre la réponse en XML (sans dépendance externe)."""

import argparse
from itertools import count
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


GAME_RELATIONS = (
    "age_ratings", "alternative_names", "bundles", "collection", "collections",
    "dlcs", "expanded_games", "expansions",
    "external_games", "forks", "franchise", "franchises", "game_engines",
    "game_localizations", "game_modes", "game_status", "game_type", "genres",
    "involved_companies", "keywords", "language_supports", "multiplayer_modes",
    "parent_game", "platforms", "player_perspectives", "ports", "release_dates",
    "remakes", "remasters", "similar_games", "standalone_expansions", "themes",
    "version_parent", "websites",
)
GAME_EXCLUDED_FIELDS = ("artworks", "checksum", "cover", "executables", "screenshots", "slug", "videos")
CHARACTER_EXCLUDED_FIELDS = ("checksum", "mug_shot", "slug")
EXCLUDED_FIELDS = {*GAME_EXCLUDED_FIELDS, *CHARACTER_EXCLUDED_FIELDS, "logo", "platform_logo"}
GAME_FIELDS = (
    "fields *," + ",".join(f"{relation}.*" for relation in GAME_RELATIONS)
    + "; exclude " + ",".join(GAME_EXCLUDED_FIELDS) + ";"
)
CHARACTER_FIELDS = (
    "fields *,character_gender.*,character_species.*; exclude "
    + ",".join(CHARACTER_EXCLUDED_FIELDS) + ";"
)
# Le type 1 correspond au score IGDB Visits.
POPULARITY_QUERY = "fields game_id; where popularity_type = 1; sort value desc;"
DEFAULT_LIMIT = 3000
PAGE_SIZE = 500
GAME_BATCH_SIZE = 100  # Les relations développées augmentent la taille des réponses.


def load_credentials():
    """Lit les deux identifiants sans les afficher ni modifier le fichier .env."""
    values = {}
    env_path = Path(__file__).resolve().with_name(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            key, separator, value = line.partition("=")
            if separator:
                values[key.strip()] = value.strip().strip("\"'")
    credentials = {}
    for key in ("client_id", "client_secret"):
        credentials[key] = os.environ.get(key) or values.get(key)
        if not credentials[key]:
            raise ValueError(f"Variable {key} manquante dans .env.")
    return credentials


def post_json(url, data, headers):
    request = Request(url, data=data, headers=headers, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_igdb_list(endpoint, query, headers):
    items = post_json(f"https://api.igdb.com/v4/{endpoint}", query.encode("utf-8"), headers)
    if not isinstance(items, list):
        raise ValueError("Réponse IGDB inattendue : une liste était attendue.")
    return items


def fetch_game_characters(game_ids, headers):
    by_game = {game_id: [] for game_id in game_ids}
    if not by_game:
        return by_game

    ids_filter = ",".join(map(str, by_game))
    for offset in count(0, PAGE_SIZE):
        sleep(0.25)
        characters = fetch_igdb_list(
            "characters",
            f"{CHARACTER_FIELDS} where games = ({ids_filter}); sort id asc; limit {PAGE_SIZE}; offset {offset};",
            headers,
        )
        for character in characters:
            for game_id in by_game.keys() & character["games"]:
                by_game[game_id].append(character)
        if len(characters) < PAGE_SIZE:
            return by_game


def remove_excluded_fields(value):
    if isinstance(value, dict):
        for field in EXCLUDED_FIELDS & value.keys():
            del value[field]
        for child in value.values():
            remove_excluded_fields(child)
    elif isinstance(value, list):
        for child in value:
            remove_excluded_fields(child)


def iter_games(query, headers):
    if query is not None:
        yield from fetch_igdb_list("games", query, headers)
        return

    exported_ids = set()
    offset = 0
    while True:
        if offset:
            sleep(0.25)  # IGDB autorise quatre requêtes par seconde.
        ranking = fetch_igdb_list(
            "popularity_primitives",
            f"{POPULARITY_QUERY} limit {PAGE_SIZE}; offset {offset};",
            headers,
        )
        game_ids = list(dict.fromkeys(
            entry["game_id"] for entry in ranking if entry["game_id"] not in exported_ids
        ))
        for start in range(0, len(game_ids), GAME_BATCH_SIZE):
            batch = game_ids[start:start + GAME_BATCH_SIZE]
            sleep(0.25)
            ids_filter = ",".join(map(str, batch))
            details = fetch_igdb_list(
                "games", f"{GAME_FIELDS} where id = ({ids_filter}); limit {len(batch)};", headers,
            )
            by_id = {game["id"]: game for game in details}
            characters_by_game = fetch_game_characters(by_id, headers)
            for game_id in batch:
                if game_id in by_id:
                    exported_ids.add(game_id)
                    game = by_id[game_id]
                    if characters := characters_by_game[game_id]:
                        game["characters"] = characters
                    remove_excluded_fields(game)
                    yield game
                    if len(exported_ids) == DEFAULT_LIMIT:
                        return
        if len(ranking) < PAGE_SIZE:
            return
        offset += PAGE_SIZE


def build_xml(key, value):
    element = ET.Element(key)
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            element.append(build_xml(child_key, child_value))
    elif isinstance(value, list):
        for item in value:
            element.append(build_xml("item", item))
    elif value is not None:
        element.text = str(value).lower() if isinstance(value, bool) else str(value)
    return element


def write_games(output, games):
    count = 0
    temporary_path = None
    try:
        with NamedTemporaryFile(mode="wb", dir=output.parent, delete=False) as stream:
            temporary_path = Path(stream.name)
            stream.write(b"<?xml version='1.0' encoding='utf-8'?>\n<games>\n")
            for count, game in enumerate(games, 1):
                element = build_xml("game", game)
                ET.indent(element, space="  ", level=1)
                stream.write(b"  " + ET.tostring(element, encoding="utf-8") + b"\n")
            stream.write(b"</games>\n")
        temporary_path.replace(output)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="Requête APICalypse IGDB (une seule requête)")
    parser.add_argument("--output", type=Path, default=Path("games.xml"), help="Fichier XML de sortie")
    args = parser.parse_args()
    try:
        credentials = load_credentials()
        token = post_json(
            "https://id.twitch.tv/oauth2/token",
            urlencode({**credentials, "grant_type": "client_credentials"}).encode(),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )["access_token"]
        games = iter_games(
            args.query,
            {"Client-ID": credentials["client_id"], "Authorization": f"Bearer {token}",
             "Content-Type": "text/plain", "Accept": "application/json"},
        )
        count = write_games(args.output, games)
        print(f"{count} jeux enregistrés dans {args.output.resolve()}")
    except HTTPError as error:
        # Ne pas afficher la requête, les en-têtes ou la réponse d'authentification.
        print(f"Erreur HTTP {error.code} lors de l'appel à {error.url.split('?')[0]}", file=sys.stderr)
        return 1
    except (URLError, OSError, ValueError, KeyError) as error:
        print(f"Échec de la requête ({type(error).__name__}). Vérifiez .env, le réseau et le chemin de sortie.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
