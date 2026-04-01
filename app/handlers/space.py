from datetime import date, datetime  # Импортируем date и datetime для работы с датами APOD.
from html import escape  # Импортируем escape, чтобы безопасно вставлять текст ошибок в HTML.

from aiogram import F, Router  # Импортируем фильтр F и класс Router для обработки команд и кнопок.
from aiogram.filters import Command  # Импортируем фильтр команд Telegram.
from aiogram.filters.command import CommandObject  # Импортируем объект команды, чтобы читать аргументы после команды.
from aiogram.types import CallbackQuery, Message  # Импортируем типы callback-запросов и сообщений.

from app.config import get_config  # Импортируем функцию загрузки настроек проекта.
from app.keyboards.inline import get_main_menu_keyboard  # Импортируем главное меню бота.
from app.services.nasa_api import FIRST_APOD_DATE, format_apod_caption, format_apod_text, get_apod, get_random_apod_date  # Импортируем функции работы с NASA APOD API.

router = Router()  # Создаём роутер для всех космических сценариев.


async def send_apod_result(message: Message, requested_date: date | None, title_prefix: str) -> None:  # Создаём вспомогательную функцию отправки APOD пользователю.
    config = get_config()  # Загружаем настройки и API-ключ NASA из файла .env.
    apod = await get_apod(config.nasa_api_key, requested_date=requested_date)  # Получаем данные APOD за нужную дату.
    media_type = str(apod.get("media_type", "")).strip().lower()  # Получаем тип медиа и приводим его к нижнему регистру.
    media_url = str(apod.get("url", "")).strip()  # Получаем ссылку на медиафайл.

    if media_type == "image" and media_url:  # Проверяем, что NASA прислала именно изображение, а не видео.
        await message.answer_photo(  # Отправляем изображение APOD как фотографию.
            photo=media_url,  # Передаём ссылку на картинку.
            caption=f"{title_prefix}\n{format_apod_caption(apod)}",  # Добавляем красивую подпись с датой и заголовком.
        )  # Завершаем отправку фотографии.
        await message.answer(format_apod_text(apod), reply_markup=get_main_menu_keyboard())  # Следом отправляем подробное описание и меню.
        return  # Завершаем функцию, потому что изображение уже отправлено.

    await message.answer(  # Если APOD оказался видео или иным медиа, отправляем его красивым текстовым сообщением.
        f"{title_prefix}\n\n{format_apod_text(apod)}",  # Показываем заголовок блока и подробный текст APOD.
        reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню под сообщением.
    )  # Завершаем отправку текстового ответа.


@router.message(Command("space_today"))  # Объявляем обработчик команды /space_today.
async def space_today_command(message: Message) -> None:  # Создаём функцию показа APOD за сегодня.
    try:  # Начинаем безопасный блок обращения к NASA API.
        await send_apod_result(message, requested_date=date.today(), title_prefix="<b>🚀 Космос сегодня</b>")  # Запрашиваем APOD за текущую дату.
    except Exception as error:  # Перехватываем возможные ошибки API.
        await message.answer(f"<b>⚠️ Не удалось получить APOD за сегодня.</b>\n{escape(str(error))}")  # Показываем дружелюбную ошибку пользователю.


@router.callback_query(F.data == "space_today")  # Обрабатываем кнопку космической картинки за сегодня.
async def space_today_callback(callback: CallbackQuery) -> None:  # Создаём функцию ответа на кнопку космоса за сегодня.
    await callback.answer()  # Закрываем индикатор нажатия кнопки.
    await space_today_command(callback.message)  # Используем уже готовую командную функцию.


@router.message(Command("space_random"))  # Объявляем обработчик команды /space_random.
async def space_random_command(message: Message) -> None:  # Создаём функцию отправки случайного APOD за последний год.
    try:  # Начинаем безопасный блок обращения к NASA API.
        random_date = get_random_apod_date()  # Выбираем случайную дату за последний год.
        await send_apod_result(message, requested_date=random_date, title_prefix="<b>🌌 Случайный космос</b>")  # Получаем и отправляем APOD за случайную дату.
    except Exception as error:  # Перехватываем возможные ошибки API.
        await message.answer(f"<b>⚠️ Не удалось получить случайный APOD.</b>\n{escape(str(error))}")  # Показываем пользователю понятную ошибку.


@router.callback_query(F.data == "space_random")  # Обрабатываем кнопку случайной космической картинки.
async def space_random_callback(callback: CallbackQuery) -> None:  # Создаём функцию ответа на кнопку случайного APOD.
    await callback.answer()  # Закрываем индикатор нажатия кнопки.
    await space_random_command(callback.message)  # Используем уже готовую функцию случайного APOD.


@router.message(Command("space_date"))  # Объявляем обработчик команды /space_date.
async def space_date_command(message: Message, command: CommandObject) -> None:  # Создаём функцию получения APOD по конкретной дате.
    raw_date = (command.args or "").strip()  # Получаем текст после команды и очищаем его от лишних пробелов.

    if not raw_date:  # Проверяем, ввёл ли пользователь дату после команды.
        await message.answer(  # Отправляем понятную инструкцию по использованию команды.
            "<b>📅 Формат команды:</b>\n"  # Показываем заголовок подсказки.
            "<code>/space_date 2025-12-31</code>\n\n"  # Показываем правильный пример команды.
            "Дата должна быть в формате <b>ГГГГ-ММ-ДД</b>.",  # Уточняем нужный формат даты.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню.
        )  # Завершаем отправку инструкции.
        return  # Завершаем обработчик, потому что даты нет.

    try:  # Начинаем блок валидации даты и обращения к API.
        requested_date = datetime.strptime(raw_date, "%Y-%m-%d").date()  # Преобразуем текст пользователя в объект даты.
    except ValueError:  # Перехватываем ошибку неправильного формата даты.
        await message.answer(  # Отправляем понятную подсказку о неверном формате.
            "<b>⚠️ Неверный формат даты.</b>\n"  # Сообщаем, что дата введена неверно.
            "Используйте формат <b>ГГГГ-ММ-ДД</b>, например: <code>/space_date 2025-12-31</code>.",  # Показываем правильный пример.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню.
        )  # Завершаем отправку ошибки формата.
        return  # Завершаем обработчик, потому что дата некорректна.

    if requested_date < FIRST_APOD_DATE:  # Проверяем, не раньше ли дата начала архива APOD.
        await message.answer(  # Сообщаем пользователю о слишком ранней дате.
            f"<b>⚠️ Слишком ранняя дата.</b>\nAPOD доступен начиная с <b>{FIRST_APOD_DATE.isoformat()}</b>.",  # Показываем минимально допустимую дату.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню.
        )  # Завершаем отправку сообщения.
        return  # Завершаем обработчик, потому что дата недопустима.

    if requested_date > date.today():  # Проверяем, не указал ли пользователь дату из будущего.
        await message.answer(  # Сообщаем пользователю, что будущее недоступно.
            "<b>⚠️ Нельзя запросить APOD из будущего.</b>",  # Показываем понятную причину ошибки.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню.
        )  # Завершаем отправку сообщения.
        return  # Завершаем обработчик, потому что дата недопустима.

    try:  # Начинаем безопасный блок обращения к NASA API.
        await send_apod_result(message, requested_date=requested_date, title_prefix="<b>📅 Космос по выбранной дате</b>")  # Отправляем APOD за дату пользователя.
    except Exception as error:  # Перехватываем возможные ошибки API.
        await message.answer(f"<b>⚠️ Не удалось получить APOD по этой дате.</b>\n{escape(str(error))}")  # Показываем пользователю понятную ошибку.


@router.callback_query(F.data == "space_date_help")  # Обрабатываем кнопку подсказки для команды по дате.
async def space_date_help_callback(callback: CallbackQuery) -> None:  # Создаём функцию показа инструкции по работе с датой.
    await callback.answer()  # Закрываем индикатор нажатия кнопки.
    await callback.message.answer(  # Отправляем пользователю подсказку по формату команды.
        "<b>📅 Чтобы получить космос по дате, отправьте команду:</b>\n\n"  # Показываем заголовок подсказки.
        "<code>/space_date 2025-12-31</code>",  # Показываем готовый пример для копирования.
        reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню.
    )  # Завершаем отправку подсказки.