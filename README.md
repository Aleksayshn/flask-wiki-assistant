# Flask Wiki Assistant

This project is a Task 1 starter for a distributed web application
assignment. It uses Flask with Jinja2 templates and is designed to run
inside an Ubuntu virtual machine while remaining accessible from the host
browser.

## Task 1 Behaviour

- `GET /` shows a simple home page with a title, description, search field, and submit button
- `POST /search` accepts the form submission
- the result page displays the submitted search term
- the result page displays the text `I have no clue!`
- the result page provides a link to return to the home page
- empty input is handled with a validation message on the home page

## Running the App

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment example:

```bash
cp .env.example .env
```

4. Start the application:

```bash
python3 app/main.py
```

5. Open the app from the host browser:

```text
http://localhost:8888
```

## Why It Works on an Ubuntu VM

The Flask application runs with:

- host set to `0.0.0.0`
- port set to `8888`

This allows the service to listen on all VM network interfaces instead of
only `127.0.0.1`.

## Project Structure

```text
app/
  main.py
  db.py
  remote_wiki.py
  config.py
  templates/
    index.html
    result.html
  static/
    style.css
sql/
  init.sql
scripts/
  wiki.py
requirements.txt
.env.example
README.md
```

## Future Extension Points

- `app/db.py` contains a placeholder repository for future MySQL caching
- `app/remote_wiki.py` contains a placeholder service for future Paramiko remote execution
- `scripts/wiki.py` is the future command-line search helper
