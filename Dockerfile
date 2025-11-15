FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi


COPY . /app

EXPOSE 9000

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:9000"]
