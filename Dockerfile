# Builds an image for running tests, either locally or in CI

FROM python:3.12-slim

WORKDIR /code
COPY . /code/
RUN python -m pip install --upgrade pip && pip install .
