"""Interroge IGDB et enregistre la réponse en XML (sans dépendance externe)."""

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


DEFAULT_QUERY = "fields name,summary,first_release_date,rating,genres.name,platforms.name; limit 10;"


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


def append_xml(parent, key, value):
    element = ET.SubElement(parent, key)
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            append_xml(element, child_key, child_value)
    elif isinstance(value, list):
        for item in value:
            append_xml(element, "item", item)
    elif value is not None:
        element.text = str(value).lower() if isinstance(value, bool) else str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Requête APICalypse IGDB")
    parser.add_argument("--output", type=Path, default=Path("games.xml"), help="Fichier XML de sortie")
    args = parser.parse_args()
    try:
        credentials = load_credentials()
        token = post_json(
            "https://id.twitch.tv/oauth2/token",
            urlencode({**credentials, "grant_type": "client_credentials"}).encode(),
            {"Content-Type": "application/x-www-form-urlencoded"},
        )["access_token"]
        games = post_json(
            "https://api.igdb.com/v4/games",
            args.query.encode("utf-8"),
            {"Client-ID": credentials["client_id"], "Authorization": f"Bearer {token}",
             "Content-Type": "text/plain", "Accept": "application/json"},
        )
        if not isinstance(games, list):
            raise ValueError("Réponse IGDB inattendue : une liste de jeux était attendue.")
        root = ET.Element("games")
        for game in games:
            append_xml(root, "game", game)
        ET.indent(root, space="  ")
        ET.ElementTree(root).write(args.output, encoding="utf-8", xml_declaration=True)
        print(f"{len(games)} jeux enregistrés dans {args.output.resolve()}")
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
