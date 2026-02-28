CREATE TABLE btc.gains (
    id SERIAL PRIMARY KEY,
    realized_gain NUMERIC(18, 8) NOT NULL,
    unrealized_gain NUMERIC(18, 8) NOT NULL
);