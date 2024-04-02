FROM python:3.11-slim AS requirements-builder

RUN mkdir /carlos/
WORKDIR /carlos/

RUN apt-get upgrade && apt-get update && apt-get install -y curl libc6-dev libpq-dev gcc
# Install Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python -
ENV PATH="${PATH}:/opt/poetry/bin"

# Copy all libraries to ensure we have all available
COPY ./lib/ /carlos/lib/

# Copy the api dependencies
COPY ./services/api/pyproject.toml ./services/api/poetry.lock* /carlos/services/api/
WORKDIR /carlos/services/api/

# We don't use pip, as it can not resolve local sub dependencies in our libs properly
RUN poetry install --without dev

FROM python:3.11-slim

RUN apt-get update && apt-get -y install libpq5

# Copy venv and set path to env
COPY --from=requirements-builder /carlos/services/api/.venv /venv
# Currently we can not tell poetry what the path of the venv will be.
# That's why we need to adapt the !# instruction with the final path
RUN sed -i 's#/carlos/services/api/.venv#/venv#' /venv/bin/uvicorn
ENV PATH /venv/bin:$PATH

# Copy run FastAPI scripts
COPY ./services/api/start-uvicorn.sh /start-uvicorn.sh
RUN chmod +x /start-uvicorn.sh

# Copy the actual project code
COPY ./services/api/ /app/

WORKDIR /app/
ENV PYTHONPATH=/app

EXPOSE 80


CMD ["/start-uvicorn.sh"]
