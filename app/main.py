"""
Main Flask application entry point.

This module creates the Flask application and defines the routes required
for Task 1 of the assignment. The code is deliberately well-commented so
that each part is easy to explain during marking or demonstration.
"""

from flask import Flask, render_template, request

from app.config import Config
from app.db import CacheRepository
from app.remote_wiki import RemoteWikiService


def create_app() -> Flask:
    """
    Build and configure the Flask application.

    The factory pattern is useful in university projects because it keeps
    setup code separate from route logic and makes the project easier to
    extend in later tasks.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # These service objects are placeholders for later assignment tasks.
    # They are initialised here so the project structure already supports
    # MySQL caching and remote execution when those features are added.
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
        """
        Display the home page.

        This route responds to GET / and shows a simple search form.
        """
        return render_template("index.html", error_message=None, previous_term="")

    @app.post("/search")
    def search():
        """
        Process the submitted search term from the home page form.

        For Task 1, the application does not perform a real search yet.
        Instead, it validates the input and then shows the required
        placeholder result: "I have no clue!"
        """
        search_term = request.form.get("search_term", "").strip()

        # If the form is submitted with an empty value, re-display the home
        # page with a clear validation message for the user.
        if not search_term:
            return render_template(
                "index.html",
                error_message="Please enter a search term before submitting.",
                previous_term="",
            ), 400

        # Placeholder calls show where future caching and remote execution
        # would be integrated. Their return values are not yet used in Task 1.
        cache_repository.get_cached_result(search_term)
        remote_wiki_service.search(search_term)

        return render_template(
            "result.html",
            search_term=search_term,
            message="I have no clue!",
        )

    return app


app = create_app()


if __name__ == "__main__":
    # The app is exposed on all network interfaces so it can be reached from
    # the host browser when running inside an Ubuntu virtual machine.
    app.run(
        host=app.config["FLASK_HOST"],
        port=app.config["FLASK_PORT"],
        debug=True,
    )
