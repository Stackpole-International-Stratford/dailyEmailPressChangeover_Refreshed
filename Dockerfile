FROM python:3

RUN apt-get install -y --no-install-recommends cron
RUN crontab /crontab

WORKDIR /usr/src/app

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . .

ENTRYPOINT cron -f
