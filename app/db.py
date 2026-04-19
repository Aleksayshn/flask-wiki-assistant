"""
Database helper layer.

This module contains a lightweight repository class that marks the place
where MySQL-based caching can be implemented in future assignment stages.
"""

from __future__ import annotations

from typing import Optional


class CacheRepository:
    """
    Placeholder repository for storing cached wiki search results in MySQL.

    The class keeps connection settings in one place so the application can
    be extended later with a real database client such as `mysql-connector`
    or `PyMySQL`.
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

    def get_cached_result(self, search_term: str) -> Optional[str]:
        """
        Return a cached result if one exists.

        For the starter project this method returns `None`. In a later
        version it can query a MySQL table and return a stored summary.
        """
        if not self.enabled or not search_term:
            return None

        # Future implementation:
        # 1. Open a MySQL connection.
        # 2. Query the cache table by search term.
        # 3. Return the cached result if found.
        return None

    def save_cached_result(self, search_term: str, result_text: str) -> None:
        """
        Save a result to the cache.

        This method is kept as a placeholder to show the intended design of
        the data access layer.
        """
        if not self.enabled or not search_term or not result_text:
            return

        # Future implementation:
        # 1. Open a MySQL connection.
        # 2. Insert or update the cache record.
        # 3. Commit the transaction.
        return None
