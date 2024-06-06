
DELETE FROM history__prices 
WHERE usd IS NULL
  AND usd_foil IS NULL
  AND usd_etched IS NULL
;



SELECT 
  cards.name,
  history.*
FROM cards 
INNER JOIN history__prices AS history
  ON history.scryfall_card_id = cards.scryfall_card_id
WHERE cards.name = 'Steam Vents';



