

# Установка и запуск
Создайте в корне приложения файл **.env** и определите в нём все переменные, указанные в [.env_example](./.env_example).

## Запуск через docker-compose

#### Собрать и запустить приложение с помощью
```sh
$ docker compose -f docker-compose.yml up -d
```



#### Перейти на swagger [http://localhost:8000/](http://localhost:8000)
```sh
http://localhost:8000/
```

<br>

#### Тесты (которых можно сказать нет)

```shell
poetry run pytest -v -W ignore
```

<br>

## Локально
#### Загрузить ЕНВы из файла .env(при локальном  смотреть коммент в [.env_example](./.env_example))

#### Установить и активировать виртуальное окружение с помощью команд:
```sh
$ python3.12 -m venv venv
$ source venv/bin/activate
```

#### Установить зависимости:
```sh
$ pip install poetry
$ poetry install
```



<br>



#### Поднять postgres без API:
```sh
$ docker compose -f docker-compose.yml up -d postgres
```



<br>

#### Прогнать миграции с помощью с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/):
```sh
$ alembic upgrade head
```


#### Запустить приложение с помощью:
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

<br>

#### Перейти на swagger [http://localhost:8000/](http://localhost:8000)
```sh
http://localhost:8000/
```

<br>


