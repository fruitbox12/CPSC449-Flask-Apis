-- $ sqlite3 users.db < users.sql

-- PRAGMA foreign_keys
-- =ON;


CREATE TABLE IF NOT EXISTS users
(
    id INTEGER primary key,
    firstName VARCHAR,
    lastName VARCHAR,
    userName VARCHAR,
    email VARCHAR,
    password VARCHAR,
);

CREATE TABLE IF NOT EXISTS followers (
	userid VARCHAR(256) NOT NULL,
	follower VARCHAR(256) NOT NULL,
	PRIMARY KEY (userid,follower)
)