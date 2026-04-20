-- MySQL schema for the Wikipedia cache table.
-- Run this script against the database used by the Flask application.

CREATE TABLE IF NOT EXISTS wiki_search_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_term VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
