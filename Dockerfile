FROM python:3.11-alpine as requirements-stage

WORKDIR /tmp

RUN apk update
RUN apk add curl postgresql-dev python3-dev gcc musl-dev libffi-dev

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-alpine

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ARG DB_HOSTNAME
ARG DB_PASSWORD

ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_HOSTNAME=$DB_HOSTNAME

COPY ./ninepanels /code/ninepanels
# see the match between copy from, copy to and the uvicorn path...
CMD ["uvicorn", "ninepanels.main:api", "--host", "0.0.0.0"]
