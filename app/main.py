"""
Main Flask application entry point.

This module creates the Flask application and defines the routes used in
the assignment. Before contacting the remote EC2 instance, the `/search`
route first checks the MySQL cache running on the second Ubuntu VM.
"""

import logging

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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # The cache repository remains in place as a future extension point for
    # the assignment, even though the current task focuses on remote lookup.
    cache_repository = CacheRepository(
        enabled=app.config["MYSQL_CACHE_ENABLED"],
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        database=app.config["DB_NAME"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
    )
    remote_wiki_service = RemoteWikiService(
        enabled=app.config["REMOTE_EXECUTION_ENABLED"],
        host=app.config["EC2_HOST"],
        port=app.config["EC2_PORT"],
        username=app.config["EC2_USERNAME"],
        key_path=app.config["EC2_KEY_PATH"],
        script_path=app.config["EC2_WIKI_SCRIPT_PATH"],
    )

    # On startup, try to create the cache table automatically. If the
    # database container is unavailable, the repository handles the failure
    # and Flask continues running.
    if cache_repository.init_cache_table_if_needed():
        app.logger.info("Cache table initialization completed.")
    elif app.config["MYSQL_CACHE_ENABLED"]:
        app.logger.warning("Cache table initialization skipped because the database is unavailable.")

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
        Process the submitted search term and return a result page.

        The application checks the local MySQL cache first. If no cached
        result exists, it then contacts the remote EC2 instance to run the
        Wikipedia helper script.
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

        cached_result = cache_repository.get_cached_result(search_term)
        if cached_result:
            app.logger.info("Cache hit for search term '%s'.", search_term)
            return render_template(
                "result.html",
                search_term=search_term,
                source="cache",
                wiki_result={
                    "success": True,
                    "title": cached_result["title"],
                    "url": cached_result["url"],
                    "summary": cached_result["summary"],
                    "raw_output": "",
                    "error": "",
                },
            )
        app.logger.info("Cache miss for search term '%s'.", search_term)

        app.logger.info("Remote wiki search started for '%s'.", search_term)
        wiki_result = remote_wiki_service.search(search_term)
        app.logger.info("Remote wiki search completed for '%s'.", search_term)

        if wiki_result["success"]:
            save_success = cache_repository.save_cached_result(
                search_term=search_term,
                title=str(wiki_result["title"]),
                url=str(wiki_result["url"]),
                summary=str(wiki_result["summary"]),
            )
            if save_success:
                app.logger.info("Cache save success for search term '%s'.", search_term)
            else:
                app.logger.warning("Cache save failure for search term '%s'.", search_term)

        return render_template(
            "result.html",
            search_term=search_term,
            source="wikipedia",
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
