-- $ sqlite3 users.db < users.sql

-- PRAGMA foreign_keys
-- =ON;



CREATE TABLE IF NOT EXISTS users
(
    id VARCHAR,
    firstName VARCHAR,
    lastName VARCHAR,
    userName VARCHAR UNIQUE,
    email VARCHAR,
    password VARCHAR,
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS followers (
	userid VARCHAR(256) NOT NULL,
	follower VARCHAR(256) NOT NULL,
	PRIMARY KEY (userid,follower)
);