from __future__ import annotations  # Включаем удобную работу с современными аннотациями типов.

from datetime import date, timedelta  # Импортируем date и timedelta для работы с датами APOD.
from html import escape  # Импортируем escape, чтобы безопасно вставлять внешний текст в HTML Telegram.
from random import randint  # Импортируем randint, чтобы выбирать случайную дату.
from typing import Any  # Импортируем Any для аннотаций данных из JSON-ответа.

import aiohttp  # Импортируем aiohttp для асинхронных HTTP-запросов.

BASE_URL = "https://api.nasa.gov/planetary/apod"  # Сохраняем адрес APOD API в отдельной константе.
FIRST_APOD_DATE = date(1995, 6, 16)  # Запоминаем самую раннюю доступную дату APOD.


async def _fetch_json(url: str, params: dict[str, Any]) -> dict[str, Any]:  # Создаём функцию запроса JSON к NASA API.
    timeout = aiohttp.ClientTimeout(total=20)  # Ограничиваем максимальное время ожидания ответа двадцатью секундами.

    async with aiohttp.ClientSession(timeout=timeout) as session:  # Открываем асинхронную HTTP-сессию.
        async with session.get(url, params=params) as response:  # Отправляем GET-запрос с параметрами.
            if response.status != 200:  # Проверяем успешность ответа сервера.
                response_text = await response.text()  # Читаем текст ответа сервера при ошибке.
                raise ValueError(f"NASA API вернул ошибку {response.status}: {response_text[:200]}")  # Показываем понятную ошибку с обрезанным ответом.

            data = await response.json()  # Преобразуем ответ сервера в JSON.

            if not isinstance(data, dict):  # Проверяем, что ответ действительно словарь.
                raise ValueError("NASA API вернул неожиданный формат ответа.")  # Сообщаем об ошибке формата.

            return data  # Возвращаем готовый словарь с данными APOD.


async def get_apod(api_key: str, requested_date: date | None = None) -> dict[str, Any]:  # Создаём функцию получения APOD за нужную дату.
    params: dict[str, Any] = {"api_key": api_key}  # Создаём словарь параметров и сразу добавляем API-ключ.

    if requested_date is not None:  # Проверяем, передана ли конкретная дата запроса.
        params["date"] = requested_date.isoformat()  # Добавляем дату в формате ГГГГ-ММ-ДД.

    return await _fetch_json(url=BASE_URL, params=params)  # Выполняем запрос и возвращаем ответ NASA API.


def get_random_apod_date() -> date:  # Создаём функцию выбора случайной даты за последний год.
    today = date.today()  # Получаем сегодняшнюю дату.
    start_date = today - timedelta(days=365)  # Вычисляем дату ровно на год раньше.
    random_days = randint(0, (today - start_date).days)  # Выбираем случайное количество дней внутри диапазона.
    return start_date + timedelta(days=random_days)  # Возвращаем случайную дату из последнего года.


def format_apod_caption(apod: dict[str, Any]) -> str:  # Создаём короткую подпись для фото APOD.
    title = escape(str(apod.get("title", "Без названия")))  # Безопасно подготавливаем заголовок APOD.
    apod_date = escape(str(apod.get("date", "Дата не указана")))  # Безопасно подготавливаем дату APOD.
    return f"<b>🌌 {title}</b>\n<b>📅 Дата:</b> {apod_date}"  # Возвращаем короткий красивый заголовок для подписи к изображению.


def format_apod_text(apod: dict[str, Any]) -> str:  # Создаём подробный текст с описанием космического объекта.
    title = escape(str(apod.get("title", "Без названия")))  # Безопасно подготавливаем заголовок APOD.
    apod_date = escape(str(apod.get("date", "Дата не указана")))  # Безопасно подготавливаем дату APOD.
    explanation = escape(str(apod.get("explanation", "Описание отсутствует.")))  # Безопасно подготавливаем описание APOD.
    media_type = escape(str(apod.get("media_type", "unknown")))  # Безопасно подготавливаем тип медиа.
    media_url = str(apod.get("url", "")).strip()  # Получаем обычную ссылку на изображение или видео.
    hd_url = str(apod.get("hdurl", "")).strip()  # Получаем ссылку на HD-версию, если она есть.
    links: list[str] = []  # Создаём список ссылок, которые покажем внизу сообщения.

    if media_url:  # Проверяем, есть ли основная ссылка на медиа.
        links.append(f'<a href="{escape(media_url)}">🔗 Открыть медиа</a>')  # Добавляем ссылку на основное медиа.

    if hd_url and hd_url != media_url:  # Проверяем, есть ли отдельная HD-ссылка и отличается ли она от основной.
        links.append(f'<a href="{escape(hd_url)}">🖼 Открыть HD-версию</a>')  # Добавляем ссылку на HD-версию.

    links_text = " | ".join(links)  # Склеиваем все ссылки в одну красивую строку.
    footer = f"\n\n{links_text}" if links_text else ""  # Формируем нижний блок со ссылками или оставляем его пустым.

    return (  # Возвращаем готовый подробный текст APOD.
        f"<b>🌌 {title}</b>\n"  # Показываем заголовок APOD.
        f"<b>📅 Дата:</b> {apod_date}\n"  # Показываем дату публикации APOD.
        f"<b>🎞 Тип медиа:</b> {media_type}\n\n"  # Показываем тип медиа, например image или video.
        f"<b>📝 Описание:</b>\n{explanation}{footer}"  # Показываем описание и доступные ссылки.
    )  # Завершаем возврат форматированного текста.