FROM python:3.11.0 as python-base

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.5.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base as telegrambot

# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy Dependencies
COPY poetry.lock pyproject.toml ./

# [OPTIONAL] Validate the project is properly configured

# Install Dependencies
RUN poetry install --no-interaction --no-cache --without dev

# Copy Application
COPY . /app

# install ffmpeg
RUN apt-get -y update && apt-get install -y ffmpeg && pip install "python-telegram-bot[webhooks]" && pip install -r requirements.txt

# Run Application
CMD [ "python3", "main.py"]

