-- View for latest value
CREATE VIEW current__price AS (
    SELECT DISTINCT ON (scryfall_card_id) * FROM history__prices 
    WHERE 
        event_timestamp = (
            SELECT MAX(event_timestamp) FROM history__prices
        )
);

