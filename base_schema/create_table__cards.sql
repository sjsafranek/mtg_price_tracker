
CREATE TABLE IF NOT EXISTS cards (
    id               UUID PRIMARY KEY,
    oracle_id        UUID,
    name             TEXT NOT NULL,
    set_code         TEXT,
    set_name         TEXT,
    collector_number TEXT,
    lang             TEXT,
    released_at      DATE,
    layout           TEXT,
    mana_cost        TEXT,
    cmc              NUMERIC,
    type_line        TEXT,
    oracle_text      TEXT,
    power            TEXT,
    toughness        TEXT,
    colors           TEXT[],
    color_identity   TEXT[],
    keywords         TEXT[],
    rarity           TEXT,
    artist           TEXT,
    prices           JSONB,
    legalities       JSONB,
    image_uris       JSONB,
    data             JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS cards_oracle_id_idx ON cards (oracle_id);
CREATE INDEX IF NOT EXISTS cards_name_idx      ON cards (lower(name));
CREATE INDEX IF NOT EXISTS cards_set_idx       ON cards (set_code, collector_number);
CREATE INDEX IF NOT EXISTS cards_data_gin_idx  ON cards USING GIN (data jsonb_path_ops);
