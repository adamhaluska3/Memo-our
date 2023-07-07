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
    birth_date DATE NOT NULL,
    event_type TEXT NOT NULL,

    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE VIEW events_data AS 
    SELECT id, author_id, created, name, birth_date, event_type, strftime('%j', birth_date) - strftime('%j', 'now') AS remaining_days FROM events;