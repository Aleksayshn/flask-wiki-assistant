# Distributed Flask Wikipedia Lookup

## Overview

This project is a distributed cloud computing assignment built with Flask,
Paramiko, MySQL, and Docker. The system allows a user to enter a search term
in a web browser, checks whether the result is already cached in MySQL, and if
not, performs a remote Wikipedia lookup on an Ubuntu EC2 instance over SSH.

The project was designed to demonstrate:

- a Flask web application running on Ubuntu VM 1
- remote execution on an EC2 Ubuntu server
- a MySQL cache running inside Docker on Ubuntu VM 2
- modular Python code suitable for an academic submission

## Architecture Overview

The application is split across three environments:

1. VM 1: Flask Web Server

This machine runs the main Flask application. It serves the user interface,
handles form submissions, checks the cache, and contacts the EC2 instance if a
remote lookup is needed.

2. EC2 Ubuntu Instance: Wikipedia Service

This machine stores and runs the remote `wiki.py` script. Flask connects to it
through SSH using Paramiko and a private key. The remote script uses the
Python `wikipedia` package and returns structured plain-text output.

3. VM 2: MySQL in Docker

This machine runs the MySQL database inside a Docker container. It stores
cached search results so repeated searches can be returned quickly without
calling the EC2 instance again.

## Technologies Used

- Python 3
- Flask
- Jinja2
- Paramiko
- mysql-connector-python
- Wikipedia Python package
- MySQL
- Docker
- Ubuntu Linux

## Folder Structure

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

## Setup

### VM 1 Flask Server

1. Clone or copy the project onto VM 1.
2. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the environment template:

```bash
cp .env.example .env
```

5. Update `.env` with the correct database and EC2 values.

6. Start the Flask application:

```bash
python -m app.main
```

The application listens on `0.0.0.0:8888`, so it can be accessed from the
host browser if the VM network is configured correctly.

### EC2 Ubuntu Wiki Server

1. Launch an Ubuntu EC2 instance.
2. Connect to the instance using SSH.
3. Create a project directory:

```bash
mkdir -p /home/ubuntu/wiki-service
cd /home/ubuntu/wiki-service
```

4. Create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

5. Install the Wikipedia dependency:

```bash
pip install wikipedia
```

6. Copy the `wiki.py` script to the EC2 instance:

```bash
scp -i /path/to/key.pem scripts/wiki.py ubuntu@<ec2-host>:/home/ubuntu/wiki-service/wiki.py
```

7. Test the script directly on EC2:

```bash
/home/ubuntu/wiki-service/venv/bin/python /home/ubuntu/wiki-service/wiki.py "Cloud computing"
```

The Flask application is configured to run the remote script with the EC2
virtual environment interpreter:

```bash
/home/ubuntu/wiki-service/venv/bin/python /home/ubuntu/wiki-service/wiki.py "<search term>"
```

### VM 2 MySQL Docker Container

1. Install Docker on VM 2.
2. Start a MySQL container and expose port `7888`:

```bash
docker run -d \
  --name wiki-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=wiki_cache \
  -e MYSQL_USER=wiki_user \
  -e MYSQL_PASSWORD=wiki_password \
  -p 7888:3306 \
  mysql:8
```

3. Copy the SQL file to VM 2 if needed, or run it directly through the MySQL client.

4. Initialize the table:

```bash
mysql -h 127.0.0.1 -P 7888 -u wiki_user -p wiki_cache < sql/init.sql
```

The Flask application can also attempt to create the cache table
automatically at startup.

## Environment Variable Configuration

Create a `.env` file on VM 1 based on `.env.example`.

Main variables:

```env
SECRET_KEY=dev-secret-key
FLASK_HOST=0.0.0.0
FLASK_PORT=8888

MYSQL_CACHE_ENABLED=true
DB_HOST=<vm2-ip-or-hostname>
DB_PORT=7888
DB_NAME=wiki_cache
DB_USER=wiki_user
DB_PASSWORD=wiki_password

REMOTE_EXECUTION_ENABLED=true
EC2_HOST=<ec2-public-dns-or-ip>
EC2_PORT=22
EC2_USERNAME=ubuntu
EC2_KEY_PATH=/path/to/your-ec2-key.pem
EC2_WIKI_SCRIPT_PATH=/home/ubuntu/wiki-service/wiki.py
```

Notes:

- `MYSQL_CACHE_ENABLED=true` enables database caching.
- `REMOTE_EXECUTION_ENABLED=true` enables SSH lookup on EC2.
- `EC2_KEY_PATH` must point to a readable private key on VM 1.
- `EC2_WIKI_SCRIPT_PATH` must match the actual script location on EC2.

## How To Install Dependencies

Install Flask-side dependencies on VM 1:

```bash
pip install -r requirements.txt
```

The main dependencies are:

- `Flask`
- `python-dotenv`
- `Paramiko`
- `mysql-connector-python`
- `wikipedia`

Install the remote dependency on EC2:

```bash
pip install wikipedia
```

## How To Run the Flask App

From VM 1:

```bash
source .venv/bin/activate
python -m app.main
```

Expected startup behaviour:

- Flask starts on `0.0.0.0:8888`
- the app attempts to initialize the cache table
- if the database is unavailable, Flask logs a warning and still continues

## How To Test From the Host Browser

1. Make sure VM 1 is running and reachable from the host machine.
2. Start Flask on VM 1.
3. Open a browser on the host machine.
4. Visit:

```text
http://<vm1-ip>:8888
```

If port forwarding is configured in the VM software, `http://localhost:8888`
may also work from the host.

Test flow:

1. Open the home page.
2. Enter a search term such as `Cloud computing`.
3. Submit the form.
4. Confirm the result page shows:
   the search term, title, URL, summary, and result source.
5. Search for the same term again.
6. Confirm the second request is returned from `cache`.

## How Caching Works

The application uses a cache-first workflow:

1. The user submits a search term.
2. Flask queries MySQL for an existing record with the same `search_term`.
3. If a record is found, Flask renders the result page with `source=cache`.
4. If no record is found, Flask starts a remote SSH lookup on EC2.
5. If the remote lookup succeeds, the result is saved into MySQL.
6. Future searches for the same term are served from the cache.

Cached fields:

- `search_term`
- `title`
- `url`
- `summary`
- `created_at`
