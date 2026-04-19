"""
Main Flask application entry point.

This module creates the Flask application and defines the routes used in
the assignment. The `/search` route now calls a remote EC2 instance through
Paramiko to run the Wikipedia helper script.
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

    # The cache repository remains in place as a future extension point for
    # the assignment, even though the current task focuses on remote lookup.
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
        host=app.config["EC2_HOST"],
        port=app.config["EC2_PORT"],
        username=app.config["EC2_USERNAME"],
        key_path=app.config["EC2_KEY_PATH"],
        script_path=app.config["EC2_WIKI_SCRIPT_PATH"],
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
        Process the submitted search term and request the result remotely.

        The local Flask app validates the form input, then SSHs into the EC2
        instance and runs `wiki.py` there. The returned plain-text output is
        converted into a Python dictionary by `RemoteWikiService`.
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

        # This placeholder call keeps the project ready for future caching.
        cache_repository.get_cached_result(search_term)
        wiki_result = remote_wiki_service.search(search_term)

        return render_template(
            "result.html",
            search_term=search_term,
            wiki_result=wiki_result,
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
