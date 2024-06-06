
-- Create cards table
CREATE TABLE cards (
    scryfall_card_id    UUID PRIMARY KEY,
    name                TEXT,
    created_at          TIMESTAMP DEFAULT (now()),
    updated_at          TIMESTAMP DEFAULT (now())
);

-- Create history table to track prices
CREATE TABLE history__prices (
    event_timestamp     TIMESTAMPTZ DEFAULT (now()),
    scryfall_card_id    UUID,
    usd                 REAL,
    usd_foil            REAL,
    usd_etched          REAL,
    PRIMARY KEY (scryfall_card_id, event_timestamp),
    FOREIGN KEY (scryfall_card_id) REFERENCES cards (scryfall_card_id)
);
SELECT create_hypertable('history__prices', by_range('event_timestamp'));
CREATE INDEX ix_card_time ON history__prices (scryfall_card_id, event_timestamp DESC);
