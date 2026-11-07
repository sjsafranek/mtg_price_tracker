
CREATE TABLE IF NOT EXISTS card_price_history (
    card_id      	UUID,
    prices          JSONB,
    action_type     VARCHAR(10) NOT NULL,
    changed_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create trigger function
CREATE OR REPLACE FUNCTION log_card_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO card_price_history (action_type, card_id, prices)
        VALUES ('INSERT', NEW.id, NEW.prices);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF (OLD.prices IS DISTINCT FROM NEW.prices) THEN
            INSERT INTO card_price_history (action_type, card_id, prices)
            VALUES ('UPDATE', OLD.id, OLD.prices);
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Bind trigger to table
CREATE TRIGGER cards_price_tracker_trigger
AFTER INSERT OR UPDATE OR DELETE ON cards
FOR EACH ROW
EXECUTE FUNCTION log_card_price_change();
