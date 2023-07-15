DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS events;
DROP VIEW IF EXISTS events_data;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    note TEXT,

    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE VIEW events_data AS 
    SELECT id, author_id, created, name, first_name, birth_date, note, 
    strftime('%j', birth_date) - strftime('%j', 'now') AS remaining_days,
    strftime('%Y', 'now') - strftime('%Y', birth_date) AS age
    FROM events;