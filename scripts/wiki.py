"""
Command-line helper script for future wiki lookups.

This script is intentionally simple for the starter project. It provides a
clear place to add Wikipedia API calls later, either locally or remotely.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Read a search term from the command line and print a placeholder."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/wiki.py <search-term>")
        return 1

    search_term = " ".join(sys.argv[1:]).strip()
    print(f"Starter wiki script received search term: {search_term}")
    print("I have no clue!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
