CREATE TABLE btc.prices (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    price NUMERIC(18, 8) NOT NULL
);