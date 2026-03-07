CREATE TABLE btc.analysis (
    date DATE NOT NULL PRIMARY KEY,
    price NUMERIC(18, 8) NOT NULL,
    signal VARCHAR NOT NULL
);