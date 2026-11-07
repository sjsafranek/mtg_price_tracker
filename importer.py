#!/usr/bin/env python3
"""
Import Scryfall bulk card data into PostgreSQL.

Usage:
    #pip install requests psycopg2-binary
    pip3 install requests
    pip3 install "psycopg[binary]"
    export DATABASE_URL="postgresql://mtguser:dev@localhost:5432/mtgdb"
    python scryfall_import.py                      # default_cards (every printing, English)
    python scryfall_import.py --type oracle_cards  # one entry per Oracle card
    python scryfall_import.py --file cards.json    # use a previously downloaded file

Bulk types: oracle_cards, unique_artwork, default_cards, all_cards, rulings

"""
import gzip
import json
import shutil
import argparse
import os
import sys
import tempfile

#import psycopg2
#from psycopg2.extras import Json, execute_values

import requests

import psycopg
from psycopg.types.json import Json


BULK_URL = "https://api.scryfall.com/bulk-data"
# Scryfall requires a descriptive User-Agent and an Accept header.
HEADERS = {
    "User-Agent": "scryfall-pg-importer/1.0",
    "Accept": "application/json;q=0.9,*/*;q=0.8",
}


BATCH_SIZE = 1000

COLUMNS = [
    "id", "oracle_id", "name", "set_code", "set_name", "collector_number",
    "lang", "released_at", "layout", "mana_cost", "cmc", "type_line",
    "oracle_text", "power", "toughness", "colors", "color_identity",
    "keywords", "rarity", "artist", "prices", "legalities", "image_uris", "data",
]

# UPSERT = f"""
# INSERT INTO cards ({", ".join(COLUMNS)}) VALUES %s
# ON CONFLICT (id) DO UPDATE SET
#     {", ".join(f"{c} = EXCLUDED.{c}" for c in COLUMNS if c != "id")}
# """

UPSERT = f"""
INSERT INTO cards ({", ".join(COLUMNS)}) VALUES ({", ".join('%s' for c in COLUMNS)})
ON CONFLICT (id) DO UPDATE SET
    {", ".join(f"{c} = EXCLUDED.{c}" for c in COLUMNS if c != "id")}
"""

UPSERT_QUERY = """
    INSERT INTO cards({", ".join(COLUMNS)}) 
    SELECT {", ".join(COLUMNS)} FROM temp_cards
    ON CONFLICT (id) 
    DO UPDATE SET
        {", ".join(f"{c} = EXCLUDED.{c}" for c in COLUMNS if c != "id")}
"""


def get_bulk_download_url(bulk_type: str) -> str:
    resp = requests.get(BULK_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    for entry in resp.json()["data"]:
        if entry["type"] == bulk_type:
            print(f"Bulk file: {entry['name']} "
                  f"({entry['compressed_size'] / 1_048_576:.0f} MB, updated {entry['updated_at']})")
            return entry["jsonl_download_uri"]
    raise SystemExit(f"Unknown bulk type: {bulk_type}")


def download(url: str, dest: str) -> None:
    print(f"Downloading '{url}'...")
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(dest, "wb") as out_writer:
            with gzip.GzipFile(fileobj=response.raw) as gzip_reader:
                shutil.copyfileobj(gzip_reader, out_writer)


def card_to_row(card: dict) -> tuple:
    faces = card.get("card_faces") or []

    # Multi-face cards often keep oracle_text / images only on the faces.
    oracle_text = card.get("oracle_text")
    if oracle_text is None and faces:
        oracle_text = "\n//\n".join(f.get("oracle_text", "") for f in faces)

    image_uris = card.get("image_uris")
    if image_uris is None and faces and faces[0].get("image_uris"):
        image_uris = faces[0]["image_uris"]

    colors = card.get("colors")
    if colors is None and faces:
        colors = faces[0].get("colors")

    return (
        card["id"],
        card.get("oracle_id"),
        card["name"],
        card.get("set"),
        card.get("set_name"),
        card.get("collector_number"),
        card.get("lang"),
        card.get("released_at"),
        card.get("layout"),
        card.get("mana_cost"),
        card.get("cmc"),
        card.get("type_line"),
        oracle_text,
        card.get("power"),
        card.get("toughness"),
        colors,
        card.get("color_identity"),
        card.get("keywords"),
        card.get("rarity"),
        card.get("artist"),
        Json(card.get("prices")),
        Json(card.get("legalities")),
        Json(image_uris),
        Json(card),
    )


# def import_cards(conn, path: str) -> int:
#     print("Importing...")
#     total = 0
#     batch = []
#     with conn.cursor() as cur, open(path, "r") as fh:
#         # Stream the top-level JSON array so we never load the whole file into memory.
#         # use_float=True avoids Decimal values that json can't serialize.
#         for line in fh:
#             card = json.loads(line)
#             batch.append(card_to_row(card))
#             if len(batch) >= BATCH_SIZE:
#                 # execute_values(cur, UPSERT, batch)
#                 cur.executemany(UPSERT, batch)
#                 conn.commit()
#                 total += len(batch)
#                 batch.clear()
#                 print(f"\r{total:,} cards imported", end="", flush=True)
#         if batch:
#             # execute_values(cur, UPSERT, batch)
#             cur.executemany(UPSERT, batch)
#             conn.commit()
#             total += len(batch)
#     print(f"\r{total:,} cards imported")
#     return total


def import_cards(conn, path: str) -> int:
    print("Importing...")
    total = 0
    batch = []
    with conn.cursor() as cur, open(path, "r") as fh:

        # 1. Create an empty unlogged staging table matching your target structure
        cur.execute("""
            CREATE TEMP TABLE temp_cards (LIKE cards INCLUDING DEFAULTS) ON COMMIT DROP;
        """)

        # 2. Stream data directly to the temp table via fast COPY protocol
        with cur.copy("COPY temp_users (id, name, status) FROM STDIN") as copy:
            for line in fh:
                card = json.loads(line)
                row = card_to_row(card)
                copy.write_row(row)
                total += 1
                print(f"\r{total:,} cards imported", end="", flush=True)
        
        # 3. Perform the bulk upsert logic entirely in the database engine
        print(UPSERT_QUERY)
        cur.execute(UPSERT_QUERY)

        conn.commit()


    print(f"\r{total:,} cards imported")
    return total



def main() -> None:
    parser = argparse.ArgumentParser(description="Import Scryfall bulk data into Postgres")
    parser.add_argument("--type", default="default_cards",
                        choices=["oracle_cards", "unique_artwork", "default_cards", "all_cards"])
    parser.add_argument("--file", help="Path to an already-downloaded bulk JSON file")
    parser.add_argument("--dsn", default=os.environ.get("DATABASE_URL"),
                        help="Postgres DSN (default: $DATABASE_URL)")
    args = parser.parse_args()

    if not args.dsn:
        sys.exit("Set DATABASE_URL or pass --dsn")

    # conn = psycopg2.connect(args.dsn)
    conn = psycopg.connect(args.dsn)
    try:
        if args.file:
            import_cards(conn, args.file)
        else:
            url = get_bulk_download_url(args.type)
            with tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, "bulk.jsonl")
                download(url, path)
                import_cards(conn, path)
    finally:
        conn.close()
        print('done')

if __name__ == "__main__":
    main()

