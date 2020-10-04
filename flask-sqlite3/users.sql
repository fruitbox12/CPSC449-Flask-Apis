-- $ sqlite3 users.db < users.sql

-- PRAGMA foreign_keys
-- =ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    id INTEGER primary key,
    firstName VARCHAR,
    lastName VARCHAR,
    userName VARCHAR,
    email VARCHAR,
    password VARCHAR,
);

DROP TABLE IF EXISTS userFollowers;
CREATE TABLE userFollowers
(
    id INTEGER primary key Foreign key references users(id),
    userName VARCHAR,
    follower VARCHAR
);