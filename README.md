# Basic Daily Email Boilerplate

requires a .env file with the following variables:
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

requires a distribution list in main.py

requires a report function that returns the report body in HTML
currently using Jinja2 templates.

## Usage

Fork this repo giving it a meaningful name

Clone:

`git clone https://github.com/cstrutton/new_report.git`

or update with:

`git pull`

build with:

`docker build -t new_report .`

run with:

`docker run -d --restart always new_report` 


