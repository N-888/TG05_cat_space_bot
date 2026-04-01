from __future__ import annotations  # Включаем удобную работу с современными аннотациями типов.

from datetime import datetime, timedelta  # Импортируем дату и интервал для простого кэширования списка пород.
from html import escape  # Импортируем escape, чтобы безопасно вставлять текст в HTML-сообщения Telegram.
from typing import Any  # Импортируем Any для аннотаций словарей из внешнего API.

import aiohttp  # Импортируем aiohttp, чтобы выполнять асинхронные HTTP-запросы.

BASE_URL = "https://api.thecatapi.com/v1"  # Сохраняем базовый адрес TheCatAPI в одной константе.
_BREEDS_CACHE: list[dict[str, Any]] = []  # Создаём кэш для списка пород, чтобы не запрашивать его слишком часто.
_BREEDS_CACHE_EXPIRES_AT: datetime | None = None  # Создаём переменную со временем истечения кэша.


async def _fetch_json(url: str, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None) -> Any:  # Создаём универсальную функцию запроса JSON к TheCatAPI.
    timeout = aiohttp.ClientTimeout(total=20)  # Ограничиваем максимальное время ожидания ответа двадцатью секундами.

    async with aiohttp.ClientSession(timeout=timeout) as session:  # Открываем асинхронную HTTP-сессию.
        async with session.get(url, headers=headers, params=params) as response:  # Отправляем GET-запрос на нужный адрес.
            if response.status != 200:  # Проверяем, что сервер ответил успешным кодом.
                response_text = await response.text()  # Читаем текст ошибки от сервера.
                raise ValueError(f"TheCatAPI вернул ошибку {response.status}: {response_text[:200]}")  # Показываем понятную ошибку с обрезанным ответом.

            return await response.json()  # Возвращаем распарсенный JSON-ответ.


async def get_cat_breeds(api_key: str) -> list[dict[str, Any]]:  # Создаём функцию, которая получает список всех пород кошек.
    global _BREEDS_CACHE, _BREEDS_CACHE_EXPIRES_AT  # Сообщаем, что будем использовать глобальные переменные кэша.
    now = datetime.utcnow()  # Получаем текущее время в UTC для проверки срока жизни кэша.

    if _BREEDS_CACHE and _BREEDS_CACHE_EXPIRES_AT and now < _BREEDS_CACHE_EXPIRES_AT:  # Проверяем, есть ли свежий кэш пород.
        return _BREEDS_CACHE  # Если кэш ещё актуален, сразу возвращаем его.

    headers = {"x-api-key": api_key}  # Подготавливаем заголовок с API-ключом TheCatAPI.
    data = await _fetch_json(url=f"{BASE_URL}/breeds", headers=headers)  # Запрашиваем список пород у внешнего API.

    if not isinstance(data, list):  # Проверяем, что API действительно вернул список пород.
        raise ValueError("Список пород пришёл в неожиданном формате.")  # Сообщаем об ошибке формата, если ответ нестандартный.

    _BREEDS_CACHE = data  # Сохраняем список пород в кэш.
    _BREEDS_CACHE_EXPIRES_AT = now + timedelta(hours=12)  # Обновляем срок действия кэша на двенадцать часов.
    return data  # Возвращаем готовый список пород.


async def get_random_cat_image(api_key: str) -> str:  # Создаём функцию для получения случайной картинки котика.
    headers = {"x-api-key": api_key}  # Подготавливаем заголовок с API-ключом.
    data = await _fetch_json(url=f"{BASE_URL}/images/search", headers=headers)  # Запрашиваем одну случайную фотографию кота.

    if not data or "url" not in data[0]:  # Проверяем, что ответ содержит ссылку на изображение.
        raise ValueError("Не удалось получить ссылку на изображение котика.")  # Показываем понятную ошибку, если данные пустые.

    return str(data[0]["url"])  # Возвращаем URL изображения как строку.


async def get_cat_image_by_breed(api_key: str, breed_id: str) -> str:  # Создаём функцию для получения картинки по идентификатору породы.
    headers = {"x-api-key": api_key}  # Подготавливаем заголовок с API-ключом.
    params = {"breed_ids": breed_id}  # Передаём идентификатор породы в параметрах запроса.
    data = await _fetch_json(url=f"{BASE_URL}/images/search", headers=headers, params=params)  # Запрашиваем картинку выбранной породы.

    if not data or "url" not in data[0]:  # Проверяем, что API вернул хотя бы одно изображение.
        raise ValueError("Для этой породы не удалось получить изображение.")  # Сообщаем понятную ошибку, если картинка не найдена.

    return str(data[0]["url"])  # Возвращаем URL найденного изображения.


def find_breed(breeds: list[dict[str, Any]], user_query: str) -> dict[str, Any] | None:  # Создаём функцию поиска породы по названию.
    normalized_query = user_query.strip().lower()  # Приводим пользовательский ввод к удобному виду для поиска.

    if not normalized_query:  # Проверяем, что пользователь вообще что-то ввёл.
        return None  # Возвращаем пустой результат, если строка пустая.

    for breed in breeds:  # Сначала пробуем найти точное совпадение по названию породы.
        breed_name = str(breed.get("name", "")).strip().lower()  # Берём название текущей породы и тоже нормализуем его.

        if breed_name == normalized_query:  # Сравниваем точное название с запросом пользователя.
            return breed  # Возвращаем найденную породу.

    for breed in breeds:  # Если точного совпадения нет, выполняем более мягкий поиск по части названия.
        breed_name = str(breed.get("name", "")).strip().lower()  # Повторно берём и нормализуем название породы.

        if normalized_query in breed_name:  # Проверяем, входит ли текст пользователя в название породы.
            return breed  # Возвращаем первое подходящее частичное совпадение.

    return None  # Возвращаем None, если порода так и не нашлась.


def format_breed_card(breed: dict[str, Any]) -> str:  # Создаём функцию красивого форматирования карточки породы.
    name = escape(str(breed.get("name", "Неизвестно")))  # Безопасно подготавливаем название породы.
    origin = escape(str(breed.get("origin", "Не указано")))  # Безопасно подготавливаем страну происхождения.
    temperament = escape(str(breed.get("temperament", "Не указано")))  # Безопасно подготавливаем темперамент.
    life_span = escape(str(breed.get("life_span", "Не указано")))  # Безопасно подготавливаем срок жизни.
    description = escape(str(breed.get("description", "Описание отсутствует")))  # Безопасно подготавливаем описание породы.
    wikipedia_url = str(breed.get("wikipedia_url", "")).strip()  # Получаем ссылку на Wikipedia, если она есть.
    wiki_line = f'\n<a href="{escape(wikipedia_url)}">🔗 Открыть статью в Wikipedia</a>' if wikipedia_url else ""  # Формируем красивую строку со ссылкой или пустую строку.

    return (  # Возвращаем готовый красивый текст карточки породы.
        f"<b>🐾 Порода:</b> {name}\n"  # Показываем название породы.
        f"<b>🌍 Происхождение:</b> {origin}\n"  # Показываем происхождение породы.
        f"<b>🧬 Темперамент:</b> {temperament}\n"  # Показываем особенности характера.
        f"<b>⏳ Продолжительность жизни:</b> {life_span} лет\n\n"  # Показываем ожидаемую продолжительность жизни.
        f"<b>📖 Описание:</b>\n{description}{wiki_line}"  # Показываем описание и ссылку на Wikipedia, если она есть.
    )  # Завершаем возврат форматированного текста.