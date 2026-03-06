ARG PYTHON_VERSION=3.14
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

ARG PIP_VERSION=26.0
ARG POETRY_VERSION=2.3.0
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/app

RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update && apt-get -y install python3-dev \
    && python -m pip install --user --upgrade pip==${PIP_VERSION} \
    && python -m pip install --user pipx \
    && python -m pipx install pytest-cov --include-deps \
    && python -m pipx install poetry==${POETRY_VERSION} \
    && apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-cache --no-root

COPY . .

RUN poetry sync --no-cache
