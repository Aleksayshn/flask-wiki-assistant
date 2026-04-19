"""
Main Flask application entry point.

This module creates the web app, loads configuration, and defines the
assignment starter routes. The structure is intentionally simple so that
future distributed features can be added without major refactoring.
"""

from flask import Flask, render_template, request

from app.config import Config
from app.db import CacheRepository
from app.remote_wiki import RemoteWikiService


def create_app() -> Flask:
    """
    Application factory used to create and configure the Flask app.

    Using a factory pattern keeps the project modular and makes testing
    easier in later assignment stages.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    cache_repository = CacheRepository(
        enabled=app.config["MYSQL_CACHE_ENABLED"],
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        database=app.config["MYSQL_DATABASE"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
    )
    remote_wiki_service = RemoteWikiService(
        enabled=app.config["REMOTE_EXECUTION_ENABLED"],
        host=app.config["REMOTE_HOST"],
        port=app.config["REMOTE_PORT"],
        username=app.config["REMOTE_USERNAME"],
        password=app.config["REMOTE_PASSWORD"],
        script_path=app.config["REMOTE_SCRIPT_PATH"],
    )

    @app.get("/")
    def index():
        """Render the initial form page."""
        return render_template("index.html")

    @app.post("/search")
    def search():
        """
        Handle the search form submission.

        For the starter assignment we intentionally return a placeholder
        result page. The supporting service objects are still initialised
        so they can be integrated in later milestones.
        """
        search_term = request.form.get("search_term", "").strip()

        # Placeholder calls to show where caching and remote execution would fit.
        cached_result = cache_repository.get_cached_result(search_term)
        remote_result = remote_wiki_service.search(search_term)

        return render_template(
            "result.html",
            search_term=search_term,
            cached_result=cached_result,
            remote_result=remote_result,
            message="I have no clue!",
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
