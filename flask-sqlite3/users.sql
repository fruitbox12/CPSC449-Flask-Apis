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
	following VARCHAR(256) NOT NULL,
	PRIMARY KEY (userid,following)
);


CREATE TABLE IF NOT EXISTS tweets (
	userid VARCHAR(256) NOT NULL,
	tweet_id VARCHAR(256) NOT NULL,
	tweet_text VARCHAR(256),
	tweet_media BLOB,
	date_of_creation DATETIME DESC NOT NULL,
	PRIMARY KEY (userid,tweet_id),
	UNIQUE (tweet_id)
);