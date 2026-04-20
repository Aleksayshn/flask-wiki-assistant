# Project Report

## Project Overview

This project is a distributed Flask web application developed for a university
assignment. Its purpose is to allow a user to enter a search term in a web
browser, retrieve Wikipedia information for that term, and display the result
through a simple web interface.

The application follows a distributed architecture rather than performing all
work on a single machine. The main Flask web application runs on one Ubuntu
virtual machine, the Wikipedia search script runs on a remote Ubuntu EC2
instance, and the MySQL cache runs on a second Ubuntu virtual machine inside a
Docker container.

The final system demonstrates:

- a Flask web interface
- remote command execution with Paramiko over SSH
- structured result parsing
- MySQL-based caching
- graceful error handling and startup logging

## System Architecture

The project is divided into three main parts:

1. Flask Application on Local VM 1

The Flask application provides the user interface. It accepts a search term,
checks whether the result already exists in the database cache, and if not,
contacts the remote EC2 machine to perform the Wikipedia lookup.

2. Remote Wikipedia Script on EC2

The remote EC2 instance stores `scripts/wiki.py`. This script uses the Python
`wikipedia` package to search Wikipedia, choose the top result, and return
plain-text structured output in a format that Flask can parse.

3. MySQL Cache on Local VM 2

The cache database stores previous search results. This avoids repeated remote
calls for the same search term and improves efficiency.

## Project Structure

```text
app/
  config.py
  db.py
  main.py
  remote_wiki.py
  static/
    style.css
  templates/
    index.html
    result.html
scripts/
  wiki.py
sql/
  init.sql
requirements.txt
.env.example
README.md
REPORT.md
```

## What I Implemented

### 1. Flask User Interface

The web application was implemented in Flask with Jinja2 templates.

The home page:

- displays the project title
- provides a short description
- contains a search input field
- contains a submit button

The result page:

- shows the user’s search term
- displays the page title returned from Wikipedia
- shows the page URL as a clickable link
- displays the summary text
- shows whether the result came from the cache or from the remote Wikipedia lookup
- provides a link to return and search again

The Flask application runs using:

```python
host="0.0.0.0", port=8888
```

This allows the site to be accessed from the host browser when running inside
an Ubuntu virtual machine.

### 2. Route Design

The application uses two main routes:

- `GET /`
  Renders the home page with the search form.

- `POST /search`
  Validates the form input, checks the cache, performs the remote lookup if
  necessary, and renders the result page.

If the user submits an empty search term, the application returns the home page
again with a validation message.

### 3. Configuration Management

All sensitive or environment-specific values are loaded from environment
variables through `app/config.py`. This keeps credentials and server details
out of the source code.

The main configuration values include:

- Flask host and port
- database host, port, name, username, and password
- EC2 host, SSH username, key path, and remote script path
- feature flags for remote execution and MySQL caching

This makes the application portable across different machines and easier to
configure for demonstration.

### 4. Remote Wikipedia Execution with Paramiko

The remote lookup logic was implemented in `app/remote_wiki.py`.

How it works:

1. Flask receives the user’s search term.
2. If the term is not found in the cache, Flask calls `RemoteWikiService`.
3. `RemoteWikiService` connects to the EC2 instance using Paramiko.
4. Authentication is done with a private key, not a hardcoded password.
5. The service runs:

```bash
python3 <remote_script_path> "<search_term>"
```

6. The service captures `stdout`, `stderr`, and the command exit status.
7. It parses the returned text into a Python dictionary.

The returned dictionary has the following structure:

```python
{
    "success": True or False,
    "title": "...",
    "url": "...",
    "summary": "...",
    "raw_output": "...",
    "error": "..."
}
```

This structure makes the Flask route simple and predictable.

### 5. Structured Wikipedia Script

The remote script `scripts/wiki.py` was rewritten as a clean command-line
utility suitable for an academic project.

Its responsibilities are:

- accept the search term from command-line arguments
- use the `wikipedia` Python package
- search Wikipedia
- prefer the top result
- return structured plain text
- limit the summary length to a suitable size for web display
- handle common Wikipedia errors cleanly

The script outputs:

```text
TITLE: ...
URL: ...
SUMMARY: ...
```

This format was chosen because it is easy to inspect manually and easy to parse
from Flask.

### 6. Robust Remote Result Parsing

The remote parser in `app/remote_wiki.py` was improved to be more defensive.

It now:

- reads labelled lines using `TITLE:`, `URL:`, and `SUMMARY:`
- supports multi-line summary output
- ignores blank lines
- ignores unrelated warnings and noisy output
- returns `raw_output` even if parsing fails

This is useful because remote command execution can sometimes include warnings,
SSH banners, or unexpected output.

### 7. MySQL Caching

Caching was implemented in `app/db.py` using `mysql-connector-python`.

The cache repository provides these functions:

- `get_db_connection()`
- `init_cache_table_if_needed()`
- `get_cached_result(search_term)`
- `save_cached_result(search_term, title, url, summary)`

The cache table stores:

- `id`
- `search_term`
- `title`
- `url`
- `summary`
- `created_at`

The `search_term` column is unique so that each search term is stored once.
If a result already exists, it can be updated using `ON DUPLICATE KEY UPDATE`.

### 8. Search Flow with Cache-First Logic

The main request flow in `app/main.py` works as follows:

1. The user enters a search term on the home page.
2. Flask validates the input.
3. Flask checks the MySQL cache first.
4. If a cached result exists:
   the result page is rendered with `source="cache"`.
5. If no cached result exists:
   Flask starts a remote Wikipedia lookup.
6. If the remote lookup succeeds:
   the result is saved into MySQL and shown with `source="wikipedia"`.
7. If the remote lookup fails:
   the result page still shows the error message and any raw output available.

This design reduces unnecessary remote calls and makes the system more
efficient.

## Database Schema

The SQL schema is stored in `sql/init.sql`.

The table definition is:

```sql
CREATE TABLE IF NOT EXISTS wiki_search_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_term VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Reliability and Error Handling

Several reliability improvements were added so the application remains usable
even when external systems are unavailable.

### Cache Table Initialization at Startup

When Flask starts, it automatically attempts to create the cache table.

If the database is unavailable:

- a warning is logged
- Flask continues running
- the application can still use remote Wikipedia lookup without caching

### Console Logging

Clear console logging was added for:

- cache hit
- cache miss
- remote wiki search started
- remote wiki search completed
- cache save success
- cache save failure

This makes it easier to demonstrate the system and explain the flow during
marking.

### Remote Execution Errors

The remote lookup service handles:

- missing configuration
- missing SSH private key
- authentication failure
- SSH errors
- operating system and network errors
- unexpected or badly formatted remote output

Instead of crashing, the service returns a structured error dictionary so the
result page can still display useful feedback.

### Wikipedia Script Errors

The remote `wiki.py` script handles:

- missing search term
- empty search term
- no search result found
- disambiguation pages
- general network or API failures

This keeps the script suitable for automation and safer to use from Flask.

## Technologies Used

- Python 3
- Flask
- Jinja2
- Paramiko
- mysql-connector-python
- wikipedia package
- MySQL
- Docker

## How the Main Components Work Together

In summary, the application works like this:

1. The user submits a term in the browser.
2. Flask receives the request.
3. Flask checks the MySQL cache.
4. If cached data exists, it is shown immediately.
5. Otherwise Flask connects to EC2 using SSH.
6. EC2 runs `wiki.py`.
7. The script queries Wikipedia and returns structured text.
8. Flask parses the response.
9. Flask stores successful results in MySQL.
10. Flask renders the result page for the user.

## Conclusion

This project demonstrates a simple but complete distributed web application
architecture for an academic assignment. It combines a Flask front end, remote
script execution over SSH, structured parsing, and MySQL caching. The code was
written to remain modular, readable, and easy to explain in a report or live
demo.

The final implementation is suitable as a starter or submission-quality
university project because it includes separation of concerns, clear comments,
error handling, and practical distributed-system behaviour.
