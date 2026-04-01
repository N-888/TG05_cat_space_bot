from __future__ import annotations  # Включаем удобную работу с аннотациями типов в современных версиях Python.

import os  # Импортируем модуль os, чтобы читать переменные окружения.
from dataclasses import dataclass  # Импортируем dataclass, чтобы удобно хранить настройки проекта.
from functools import lru_cache  # Импортируем lru_cache, чтобы не перечитывать .env много раз подряд.
from pathlib import Path  # Импортируем Path, чтобы удобно собирать пути к файлам.

from dotenv import load_dotenv  # Импортируем load_dotenv, чтобы загружать переменные из файла .env.

BASE_DIR = Path(__file__).resolve().parent.parent  # Определяем корневую папку проекта.
ENV_FILE = BASE_DIR / ".env"  # Собираем путь к файлу .env в корне проекта.
load_dotenv(ENV_FILE)  # Загружаем переменные окружения из файла .env.


@dataclass(slots=True)  # Создаём компактный dataclass для хранения всех настроек проекта.
class Config:  # Описываем структуру конфигурации бота.
    bot_token: str  # Храним токен Telegram-бота.
    the_cat_api_key: str  # Храним API-ключ для TheCatAPI.
    nasa_api_key: str  # Храним API-ключ для NASA APOD API.


@lru_cache(maxsize=1)  # Кэшируем результат, чтобы настройки читались один раз за запуск.
def get_config() -> Config:  # Создаём функцию, которая возвращает готовый объект настроек.
    bot_token = os.getenv("BOT_TOKEN", "").strip()  # Читаем токен Telegram-бота и убираем лишние пробелы.
    the_cat_api_key = os.getenv("THE_CAT_API_KEY", "").strip()  # Читаем ключ TheCatAPI и убираем лишние пробелы.
    nasa_api_key = os.getenv("NASA_API_KEY", "").strip()  # Читаем ключ NASA API и убираем лишние пробелы.
    missing_values: list[str] = []  # Создаём список для названий незаполненных переменных.

    if not bot_token:  # Проверяем, заполнен ли токен Telegram-бота.
        missing_values.append("BOT_TOKEN")  # Добавляем имя отсутствующей переменной в список.

    if not the_cat_api_key:  # Проверяем, заполнен ли ключ TheCatAPI.
        missing_values.append("THE_CAT_API_KEY")  # Добавляем имя отсутствующей переменной в список.

    if not nasa_api_key:  # Проверяем, заполнен ли ключ NASA API.
        missing_values.append("NASA_API_KEY")  # Добавляем имя отсутствующей переменной в список.

    if missing_values:  # Проверяем, есть ли незаполненные значения.
        missing_text = ", ".join(missing_values)  # Склеиваем имена отсутствующих переменных в одну строку.
        raise ValueError(f"В файле .env не заполнены переменные: {missing_text}")  # Останавливаем запуск и показываем понятную ошибку.

    return Config(bot_token=bot_token, the_cat_api_key=the_cat_api_key, nasa_api_key=nasa_api_key)  # Возвращаем готовый объект конфигурации.