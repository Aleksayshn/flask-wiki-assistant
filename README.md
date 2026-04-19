# Flask Wiki Assistant

Starter project for a distributed web application assignment using Flask,
Jinja2 templates, and a modular Python structure.

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

## Features

- Flask app configured to run on `0.0.0.0:8888`
- Home page with a search form
- Result page that displays `I have no clue!`
- Modular design with separate configuration, database, and remote service layers
- Placeholder code for future Paramiko SSH execution
- Placeholder code for future MySQL caching

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file:

```bash
cp .env.example .env
```

4. Run the Flask application:

```bash
python app/main.py
```

5. Open the application in your browser:

```text
http://localhost:8888
```

## Database Placeholder

The file `sql/init.sql` contains a starter MySQL table for caching search
results. The current project does not yet perform database reads or writes.

## Remote Execution Placeholder

The file `app/remote_wiki.py` contains a placeholder service class for future
SSH-based remote script execution using Paramiko.

## Notes for Extension

- Add Wikipedia API logic to `scripts/wiki.py`
- Implement SSH execution logic in `app/remote_wiki.py`
- Implement MySQL queries in `app/db.py`
- Replace the placeholder result page with real remote or cached responses
