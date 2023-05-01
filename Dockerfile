FROM python:slim

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "/app/hass-watchdog.py"]

