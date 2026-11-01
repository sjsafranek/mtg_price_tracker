#!/usr/bin/env python3
"""
Import Scryfall bulk card data into PostgreSQL.

Usage:
    pip install requests psycopg2-binary
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

import psycopg2
import requests
from psycopg2.extras import Json, execute_values


BULK_URL = "https://api.scryfall.com/bulk-data"
# Scryfall requires a descriptive User-Agent and an Accept header.
HEADERS = {
    "User-Agent": "scryfall-pg-importer/1.0",
    "Accept": "application/json;q=0.9,*/*;q=0.8",
}
BATCH_SIZE = 1000


# SCHEMA = """
# CREATE TABLE IF NOT EXISTS cards (
#     id               UUID PRIMARY KEY,
#     oracle_id        UUID,
#     name             TEXT NOT NULL,
#     set_code         TEXT,
#     set_name         TEXT,
#     collector_number TEXT,
#     lang             TEXT,
#     released_at      DATE,
#     layout           TEXT,
#     mana_cost        TEXT,
#     cmc              NUMERIC,
#     type_line        TEXT,
#     oracle_text      TEXT,
#     power            TEXT,
#     toughness        TEXT,
#     colors           TEXT[],
#     color_identity   TEXT[],
#     keywords         TEXT[],
#     rarity           TEXT,
#     artist           TEXT,
#     prices           JSONB,
#     legalities       JSONB,
#     image_uris       JSONB,
#     data             JSONB NOT NULL
# );
# CREATE INDEX IF NOT EXISTS cards_oracle_id_idx ON cards (oracle_id);
# CREATE INDEX IF NOT EXISTS cards_name_idx      ON cards (lower(name));
# CREATE INDEX IF NOT EXISTS cards_set_idx       ON cards (set_code, collector_number);
# CREATE INDEX IF NOT EXISTS cards_data_gin_idx  ON cards USING GIN (data jsonb_path_ops);


# CREATE TABLE IF NOT EXISTS card_price_history (
#     card_id      	UUID,
#     prices          JSONB,
#     action_type     VARCHAR(10) NOT NULL,
#     changed_at      TIMESTAMP NOT NULL DEFAULT NOW()
# );

# -- Create trigger function
# CREATE OR REPLACE FUNCTION log_card_price_change()
# RETURNS TRIGGER AS $$
# BEGIN
#     IF (TG_OP = 'INSERT') THEN
#         INSERT INTO card_price_history (action_type, card_id, prices)
#         VALUES ('INSERT', NEW.id, NEW.prices);
#         RETURN NEW;
#     ELSIF (TG_OP = 'UPDATE') THEN
#         IF (OLD.prices IS DISTINCT FROM NEW.prices) THEN
#             INSERT INTO card_price_history (action_type, card_id, prices)
#             VALUES ('UPDATE', OLD.id, OLD.prices);
#         END IF;
#         RETURN NEW;
#     END IF;
#     RETURN NULL;
# END;
# $$ LANGUAGE plpgsql;

# -- Bind trigger to table
# CREATE TRIGGER cards_price_tracker_trigger
# BEFORE INSERT OR UPDATE OR DELETE ON cards
# FOR EACH ROW
# EXECUTE FUNCTION log_card_price_change();


# """

COLUMNS = [
    "id", "oracle_id", "name", "set_code", "set_name", "collector_number",
    "lang", "released_at", "layout", "mana_cost", "cmc", "type_line",
    "oracle_text", "power", "toughness", "colors", "color_identity",
    "keywords", "rarity", "artist", "prices", "legalities", "image_uris", "data",
]

UPSERT = f"""
INSERT INTO cards ({", ".join(COLUMNS)}) VALUES %s
ON CONFLICT (id) DO UPDATE SET
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
            # for chunk in response.iter_content(chunk_size=1 << 20):
            #     fh.write(chunk)
            with gzip.GzipFile(fileobj=response.raw) as gzip_reader:
                # uncompressed_data = gzipped_file.read()       
                # fh.write(uncompressed_data)
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


def import_cards(conn, path: str) -> int:
    print("Importing...")
    total = 0
    batch = []
    with conn.cursor() as cur, open(path, "r") as fh:
        # Stream the top-level JSON array so we never load the whole file into memory.
        # use_float=True avoids Decimal values that json can't serialize.
        for line in fh:
            card = json.loads(line)
            batch.append(card_to_row(card))
            if len(batch) >= BATCH_SIZE:
                execute_values(cur, UPSERT, batch)
                conn.commit()
                total += len(batch)
                batch.clear()
                print(f"\r{total:,} cards imported", end="", flush=True)
        if batch:
            execute_values(cur, UPSERT, batch)
            conn.commit()
            total += len(batch)
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

    conn = psycopg2.connect(args.dsn)
    try:
        # with conn.cursor() as cur:
        #     cur.execute(SCHEMA)
        # conn.commit()

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