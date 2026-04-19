-- Initial database schema for a future MySQL cache layer.
-- This file can be executed after creating the target database.

CREATE TABLE IF NOT EXISTS wiki_search_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_term VARCHAR(255) NOT NULL UNIQUE,
    result_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
