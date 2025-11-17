Hotel Service API.

API-сервис для бронирования отелей.
Проект включает работу с пользователями, отелями, комнатами, бронированиями, JWT-аутентификацию, автоматизированные тесты и CI-pipeline на GitHub Actions.



Функциональность проекта.

Пользователи:
- Регистрация
- Логин (JWT)
- Обновление токена
- Получение своего профиля (/api/users/me/)

Бронирование:
-Просмотр отелей
-Просмотр комнат
-Создание брони
-Просмотр своих броней



Быстрый запуск проекта.

1. Клонируйте репозиторий
git clone https://github.com/Bystender-st/first_project.git
cd first_project

2. Создайте файл окружения .env

В корне проекта должен быть файл .env с содержимым:
    POSTGRES_DB=hotel_db
    POSTGRES_USER=hotel_user
    POSTGRES_PASSWORD=hotel_password
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    POSTGRES_TEST_DB=hotel_test
    DJANGO_DEBUG=True
    DJANGO_SECRET_KEY=dj_pass_12
    DJANGO_ALLOWED_HOSTS=*

3. Запуск проекта с Docker

Проект целиком работает в Docker, вам не обязательно устанавливать Python и зависимости.
Необходимо:
- Остановить предыдущие контейнеры (если были):
    docker compose down

- Пересобрать и поднять сервисы:
    docker compose up -d --build

- Проверить, что контейнеры работают:
    docker compose ps

- Проект будет доступен по адресу:
    http://localhost:9000

4. Запуск тестов

Тесты запускаются в отдельном контейнере:

    docker compose run --rm tests

Либо автоматически при сборке docker-compose.



CI/CD с GitHub Actions

В проекте настроен CI:

- Запуск линтера Ruff

- Запуск pytest

- Проверка сборки

Файл CI находится в:

    .github/workflows/ci.yml



Документация API

Swagger доступен по ссылке:

    http://localhost:9000/swagger/



Технологии

- Python 3.11

- Django 5

- Django REST Framework

- Postgres

- Docker / Docker Compose

- Pytest

- GitHub Actions

- JWT (SimpleJWT)
