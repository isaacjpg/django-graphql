FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /api

WORKDIR /api

COPY . /api/

RUN pip install -r requirements.txt


