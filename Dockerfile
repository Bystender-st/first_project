FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.1.3"

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
     && poetry install --no-interaction --no-ansi


COPY . /app

EXPOSE 9000

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:9000"]
