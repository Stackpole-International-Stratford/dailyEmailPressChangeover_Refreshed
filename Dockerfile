FROM python:3.7

RUN apt-get update && apt-get -y install cron
WORKDIR /app

ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

COPY . .

RUN echo $PYTHONPATH
# run crond as main process of container
CMD ["cron", "-f"]