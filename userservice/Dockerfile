FROM python:slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /userservice

COPY requirements.txt /userservice/

RUN pip install -r requirements.txt

COPY . /userservice/