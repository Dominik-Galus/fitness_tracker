# python3 -m build
from python:3.13-alpine

WORKDIR /usr/src/fitness_tracker

COPY ./dist /usr/src/fitness_tracker/dist

RUN apk add --no-cache build-base

RUN pip install --no-cache-dir /usr/src/fitness_tracker/dist/*.whl

EXPOSE 8000

ENTRYPOINT ["uvicorn", "fitness_tracker.main:fitness_app", "--host", "0.0.0.0", "--reload"]
