
--DROP TABLE IF EXISTS uploads;

CREATE TABLE uploads (
	filename         VARCHAR(126) PRIMARY KEY,
	uploaded_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
