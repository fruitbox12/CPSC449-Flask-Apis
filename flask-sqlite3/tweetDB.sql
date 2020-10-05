
CREATE TABLE IF NOT EXISTS tweets (
	userid VARCHAR(256) NOT NULL,
	tweet_id VARCHAR(256) NOT NULL,
	tweet_text VARCHAR(256),
	tweet_media BLOB,
	date_of_creation DATETIME DESC NOT NULL,
	PRIMARY KEY (userid,tweet_id),
	UNIQUE (tweet_id)
)
