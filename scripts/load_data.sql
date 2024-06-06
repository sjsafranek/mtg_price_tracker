---------------------
-- Load base data
---------------------


-- Cards
CREATE TEMPORARY TABLE temp (scryfall_card_id UUID, name TEXT);

\copy temp (scryfall_card_id, name)  FROM 'data/cards.csv' DELIMITER ',' CSV HEADER;

INSERT INTO cards (scryfall_card_id, name) 
	SELECT 
		temp.scryfall_card_id, 
		temp.name 
	FROM temp 
	WHERE
		NOT EXISTS (
			SELECT scryfall_card_id FROM cards WHERE cards.scryfall_card_id = temp.scryfall_card_id
		)
;

DROP TABLE temp;



-- History
CREATE TEMPORARY TABLE temp (event_timestamp TIMESTAMPTZ, scryfall_card_id UUID, usd REAL, usd_foil REAL, usd_etched REAL);

\copy temp (event_timestamp, scryfall_card_id, usd, usd_foil, usd_etched)  FROM 'data/prices.csv' DELIMITER ',' CSV HEADER;

INSERT INTO history__prices (event_timestamp, scryfall_card_id, usd, usd_foil, usd_etched) 
	SELECT 
		temp.event_timestamp, 
		temp.scryfall_card_id, 
		temp.usd, 
		temp.usd_foil, 
		temp.usd_etched
	FROM temp 
	WHERE
		(
			temp.usd IS NOT NULL
			OR temp.usd_foil IS NOT NULL
			OR temp.usd_etched IS NOT NULL
		)
		AND NOT EXISTS (
			SELECT 
				temp.scryfall_card_id 
			FROM current__price AS current 
			WHERE 
				current.scryfall_card_id = temp.scryfall_card_id 
			AND current.event_timestamp = temp.event_timestamp				
			AND COALESCE(current.usd, 0) = COALESCE(temp.usd, 0)
			AND COALESCE(current.usd_foil, 0) = COALESCE(temp.usd_foil, 0)
			AND COALESCE(current.usd_etched, 0) = COALESCE(temp.usd_etched, 0)
		)
;

DROP TABLE temp;

