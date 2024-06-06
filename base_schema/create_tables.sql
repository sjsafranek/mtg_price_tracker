CREATE TABLE "cards" (
  "scryfall_card_id"  VARCHAR(36) PRIMARY KEY,
  "name"              TEXT,
  "created_at"        TIMESTAMP DEFAULT (now()),
  "updated_at"        TIMESTAMP DEFAULT (now())
);

CREATE TABLE "history__prices" (
  "event_timestamp"   TIMESTAMPTZ DEFAULT (now()),
  "scryfall_card_id"  VARCHAR(36),
  "usd"               REAL,
  "usd_foil"          REAL,
  "usd_etched"        REAL,
  PRIMARY KEY ("scryfall_card_id", "event_timestamp")
);

ALTER TABLE "history__prices" ADD FOREIGN KEY ("scryfall_card_id") REFERENCES "cards" ("scryfall_card_id");

SELECT create_hypertable('history__prices', by_range('event_timestamp'));
CREATE INDEX ix_card_time ON history__prices (scryfall_card_id, event_timestamp DESC);


-- View for latest value
CREATE VIEW current__price AS (
  SELECT DISTINCT ON (scryfall_card_id) * FROM history__prices 
  WHERE 
    event_timestamp = (
      SELECT MAX(event_timestamp) FROM history__prices
    )
);

