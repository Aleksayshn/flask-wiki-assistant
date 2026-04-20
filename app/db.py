"""
MySQL cache layer for the distributed Flask application.

This module is responsible for storing and retrieving Wikipedia results so
the application does not need to contact the remote EC2 instance for every
search. The code is defensive so the Flask app can continue to work even if
the database container is temporarily unavailable.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import mysql.connector
from mysql.connector import Error


LOGGER = logging.getLogger(__name__)


class CacheRepository:
    """
    Repository class used to access the MySQL cache table.

    Keeping database logic in one class makes the Flask route easier to read
    and keeps the assignment structure modular.
    """

    def __init__(
        self,
        enabled: bool,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> None:
        self.enabled = enabled
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def get_db_connection(self):
        """
        Create and return a MySQL connection.

        A separate helper function keeps connection details in one place and
        makes exception handling easier to manage.
        """
        if not self.enabled:
            return None

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            connection_timeout=5,
        )

    def init_cache_table_if_needed(self) -> bool:
        """
        Ensure the cache table exists before the application uses it.

        If the database is unavailable, the error is logged and the Flask app
        continues to run without caching.
        """
        if not self.enabled:
            return False

        connection = None
        cursor = None

        try:
            connection = self.get_db_connection()
            if connection is None:
                return

            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS wiki_search_cache (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    search_term VARCHAR(255) NOT NULL UNIQUE,
                    title VARCHAR(255) NOT NULL,
                    url VARCHAR(512) NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()
            return True
        except Error as error:
            LOGGER.warning("Could not initialise cache table: %s", error)
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def get_cached_result(self, search_term: str) -> Optional[Dict[str, str]]:
        """
        Return a cached result dictionary if the search term already exists.

        Returning `None` signals a cache miss or a temporary database issue,
        allowing the Flask app to fall back to the remote Wikipedia lookup.
        """
        if not self.enabled or not search_term:
            return None

        connection = None
        cursor = None

        try:
            connection = self.get_db_connection()
            if connection is None:
                return None

            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT search_term, title, url, summary
                FROM wiki_search_cache
                WHERE search_term = %s
                """,
                (search_term,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "search_term": row["search_term"],
                "title": row["title"],
                "url": row["url"],
                "summary": row["summary"],
            }
        except Error as error:
            LOGGER.warning("Cache lookup failed for '%s': %s", search_term, error)
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def save_cached_result(
        self, search_term: str, title: str, url: str, summary: str
    ) -> bool:
        """
        Save a successful remote result in the cache.

        `ON DUPLICATE KEY UPDATE` keeps the latest value for a search term
        while preserving a simple unique-key design.
        """
        if not self.enabled or not search_term or not title or not summary:
            return False

        connection = None
        cursor = None

        try:
            connection = self.get_db_connection()
            if connection is None:
                return

            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO wiki_search_cache (search_term, title, url, summary)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    url = VALUES(url),
                    summary = VALUES(summary)
                """,
                (search_term, title, url, summary),
            )
            connection.commit()
            return True
        except Error as error:
            LOGGER.warning("Could not save cache entry for '%s': %s", search_term, error)
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
