CREATE TABLE IF NOT EXISTS users
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userName VARCHAR UNIQUE,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS followers (
	userid INTEGER NOT NULL,
	following INTEGER NOT NULL,
	FOREIGN KEY (userid) REFERENCES users (id),
	FOREIGN KEY (following) REFERENCES users (id),
	PRIMARY KEY (userid,following)
);

CREATE TABLE IF NOT EXISTS tweets (
	tweet_id INTEGER PRIMARY KEY,
	userid INTEGER,
	tweet_text VARCHAR,
	date_of_creation DATETIME DESC NOT NULL
);