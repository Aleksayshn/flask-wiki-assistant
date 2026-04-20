"""
Wikipedia command-line helper script.

This script is designed for a university assignment where Flask may call a
separate Python process to retrieve Wikipedia content. The output is plain
text and intentionally structured so that a Flask route can parse it later.
"""

from __future__ import annotations

import sys
from typing import Iterable

import wikipedia
from wikipedia import exceptions as wikipedia_exceptions


# A short summary is easier to display on a web page than a full article.
SUMMARY_SENTENCE_COUNT = 6


def clean_text(value: str) -> str:
    """
    Remove extra whitespace so each output field stays on a clean single line.

    This helps future Flask parsing because the output format remains
    predictable even when the Wikipedia text contains line breaks.
    """
    return " ".join(value.split())


def format_output(title: str, url: str, summary: str) -> str:
    """
    Build structured plain-text output.

    The labels are simple on purpose so they can be split and parsed in a
    later Flask or remote-execution task.
    """
    return "\n".join(
        [
            f"TITLE: {clean_text(title)}",
            f"URL: {clean_text(url)}",
            f"SUMMARY: {clean_text(summary)}",
        ]
    )


def format_disambiguation_options(options: Iterable[str], limit: int = 5) -> str:
    """
    Prepare a short list of disambiguation options for user-friendly output.

    Only a few options are shown so the text remains suitable for web display.
    """
    short_list = list(options)[:limit]
    return ", ".join(short_list)


def fetch_wikipedia_result(search_term: str) -> str:
    """
    Search Wikipedia and return structured output for the top matching page.

    The script first performs a search and then requests the top result as a
    full page so we can retrieve its title, URL, and summary.
    """
    # Search returns a list of candidate page titles ranked by relevance.
    matches = wikipedia.search(search_term, results=5)

    if not matches:
        return format_output(
            title="No result found",
            url="N/A",
            summary=(
                "No Wikipedia page was found for the supplied search term. "
                "Please try a different or more specific query."
            ),
        )

    top_match = matches[0]

    # `auto_suggest=False` keeps the result tied to the chosen search match.
    page = wikipedia.page(top_match, auto_suggest=False)
    summary = wikipedia.summary(page.title, sentences=SUMMARY_SENTENCE_COUNT, auto_suggest=False)

    return format_output(
        title=page.title,
        url=page.url,
        summary=summary,
    )


def main() -> int:
    """
    Parse command-line input, call Wikipedia, and print structured output.

    The function returns an exit code so it behaves like a clean production
    command-line utility.
    """
    if len(sys.argv) < 2:
        print(
            format_output(
                title="Missing search term",
                url="N/A",
                summary="No search term was provided. Usage: python3 scripts/wiki.py <search-term>",
            )
        )
        return 1

    search_term = " ".join(sys.argv[1:]).strip()

    if not search_term:
        print(
            format_output(
                title="Empty search term",
                url="N/A",
                summary="The supplied search term was empty. Please provide a valid topic to search for.",
            )
        )
        return 1

    try:
        print(fetch_wikipedia_result(search_term))
        return 0
    except wikipedia_exceptions.DisambiguationError as error:
        options_text = format_disambiguation_options(error.options)
        print(
            format_output(
                title="Disambiguation page",
                url="N/A",
                summary=(
                    f"The search term '{search_term}' is ambiguous on Wikipedia. "
                    f"Possible matches include: {options_text}. Please search again with a more specific term."
                ),
            )
        )
        return 0
    except wikipedia_exceptions.PageError:
        print(
            format_output(
                title="No result found",
                url="N/A",
                summary=(
                    f"Wikipedia did not return a page for '{search_term}'. "
                    "Please try another search term."
                ),
            )
        )
        return 0
    except Exception as error:
        # Catch network failures or third-party API/library issues so the
        # script always exits with readable output instead of a traceback.
        print(
            format_output(
                title="Wikipedia service error",
                url="N/A",
                summary=(
                    "A network or Wikipedia API issue prevented the search from completing. "
                    f"Technical detail: {clean_text(str(error)) or 'Unknown error'}."
                ),
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
