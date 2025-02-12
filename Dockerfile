from python:3.13-alpine

WORKDIR /usr/src/study_planner

COPY ./dist /usr/src/study_planner/dist

RUN apk add --no-cache build-base

RUN pip install --no-cache-dir /usr/src/study_planner/dist/*.whl

EXPOSE 8000

ENTRYPOINT ["uvicorn", "study_planner.backend.main:planner_app", "--host", "0.0.0.0", "--reload"]
