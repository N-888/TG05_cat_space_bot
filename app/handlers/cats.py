from html import escape  # Импортируем escape, чтобы безопасно показывать текст ошибок в HTML.

from aiogram import F, Router  # Импортируем фильтр F и класс Router для обработки событий.
from aiogram.filters import Command  # Импортируем фильтр команд Telegram.
from aiogram.filters.command import CommandObject  # Импортируем объект команды, чтобы читать аргументы после команды.
from aiogram.fsm.context import FSMContext  # Импортируем контекст состояния для пошагового диалога.
from aiogram.types import CallbackQuery, Message  # Импортируем типы callback-запросов и сообщений.

from app.config import get_config  # Импортируем функцию чтения конфигурации проекта.
from app.keyboards.inline import get_cancel_keyboard, get_main_menu_keyboard  # Импортируем клавиатуру отмены и главное меню.
from app.services.cat_api import find_breed, format_breed_card, get_cat_breeds, get_cat_image_by_breed, get_random_cat_image  # Импортируем функции работы с TheCatAPI.
from app.states.forms import BreedForm  # Импортируем состояние ожидания названия породы.

router = Router()  # Создаём роутер для всех кошачьих сценариев.


async def send_breed_result(message: Message, breed_query: str) -> None:  # Создаём вспомогательную функцию отправки результата по породе.
    config = get_config()  # Загружаем настройки и API-ключи из .env.
    breeds = await get_cat_breeds(config.the_cat_api_key)  # Получаем список всех пород через TheCatAPI.
    breed = find_breed(breeds, breed_query)  # Пытаемся найти нужную породу по тексту пользователя.

    if breed is None:  # Проверяем, удалось ли найти подходящую породу.
        await message.answer(  # Отправляем понятное сообщение об отсутствии результата.
            "<b>😿 Порода не найдена.</b>\n\n"  # Сообщаем, что совпадение не найдено.
            "Попробуйте написать название точнее, например: <b>Bengal</b>, <b>Siamese</b>, <b>Maine Coon</b>.",  # Подсказываем примеры корректного ввода.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню для быстрого продолжения.
        )  # Завершаем отправку сообщения.
        return  # Прерываем функцию, потому что дальше работать не с чем.

    breed_id = str(breed.get("id", "")).strip()  # Достаём идентификатор найденной породы.

    if not breed_id:  # Проверяем, есть ли у породы корректный идентификатор.
        raise ValueError("У найденной породы отсутствует идентификатор для загрузки изображения.")  # Останавливаем выполнение с понятной ошибкой.

    image_url = await get_cat_image_by_breed(config.the_cat_api_key, breed_id)  # Получаем картинку именно этой породы.
    caption = format_breed_card(breed)  # Формируем красивую карточку с описанием породы.
    await message.answer_photo(photo=image_url, caption=caption, reply_markup=get_main_menu_keyboard())  # Отправляем фото с текстом и главным меню.


@router.message(Command("cat_random"))  # Объявляем обработчик команды /cat_random.
async def cat_random_command(message: Message) -> None:  # Создаём функцию отправки случайного котика по команде.
    config = get_config()  # Загружаем настройки проекта.

    try:  # Начинаем блок безопасного обращения к внешнему API.
        image_url = await get_random_cat_image(config.the_cat_api_key)  # Получаем URL случайной фотографии котика.
        await message.answer_photo(  # Отправляем найденную фотографию в чат.
            photo=image_url,  # Передаём ссылку на изображение котика.
            caption="<b>🐱 Ловите случайного котика!</b>",  # Добавляем короткую красивую подпись.
            reply_markup=get_main_menu_keyboard(),  # Добавляем главное меню под ответом.
        )  # Завершаем отправку фотографии.
    except Exception as error:  # Перехватываем любые проблемы при работе с API.
        await message.answer(f"<b>⚠️ Не удалось получить котика.</b>\n{escape(str(error))}")  # Показываем человеку понятную ошибку.


@router.callback_query(F.data == "cat_random")  # Обрабатываем нажатие кнопки случайного котика.
async def cat_random_callback(callback: CallbackQuery) -> None:  # Создаём функцию ответа на кнопку случайного котика.
    await callback.answer()  # Закрываем индикатор нажатия кнопки.
    await cat_random_command(callback.message)  # Используем уже готовую функцию отправки случайного котика.


@router.message(Command("cat_breed"))  # Объявляем обработчик команды /cat_breed.
async def cat_breed_command(message: Message, state: FSMContext, command: CommandObject) -> None:  # Создаём функцию поиска породы по команде и аргументу.
    breed_query = (command.args or "").strip()  # Забираем текст после команды и очищаем его от лишних пробелов.

    if breed_query:  # Проверяем, передал ли пользователь породу сразу после команды.
        try:  # Начинаем безопасный блок запроса к внешнему API.
            await state.clear()  # На всякий случай очищаем старое состояние диалога.
            await send_breed_result(message, breed_query)  # Сразу ищем породу и отправляем результат.
        except Exception as error:  # Перехватываем возможные ошибки запроса.
            await message.answer(f"<b>⚠️ Не удалось найти породу.</b>\n{escape(str(error))}")  # Показываем аккуратную ошибку пользователю.

        return  # Завершаем обработчик, потому что дальнейший ввод не нужен.

    await state.set_state(BreedForm.waiting_for_breed)  # Переводим пользователя в состояние ожидания названия породы.
    await message.answer(  # Просим пользователя ввести название породы.
        "<b>🔎 Введите название породы кошки</b>\n\n"  # Показываем заголовок шага.
        "Например: <b>Bengal</b>, <b>Siamese</b>, <b>Maine Coon</b>.",  # Даём понятные примеры ввода.
        reply_markup=get_cancel_keyboard(),  # Добавляем клавиатуру отмены ввода.
    )  # Завершаем отправку инструкции.


@router.callback_query(F.data == "cat_breed")  # Обрабатываем кнопку поиска породы.
async def cat_breed_callback(callback: CallbackQuery, state: FSMContext) -> None:  # Создаём функцию запуска пошагового поиска породы по кнопке.
    await callback.answer()  # Закрываем индикатор нажатия кнопки.
    await state.set_state(BreedForm.waiting_for_breed)  # Переводим пользователя в состояние ожидания названия породы.
    await callback.message.answer(  # Просим пользователя написать название нужной породы.
        "<b>🔎 Напишите название породы кошки</b>\n\n"  # Показываем заголовок действия.
        "Например: <b>Bengal</b>, <b>Abyssinian</b>, <b>Sphynx</b>.",  # Показываем примеры, чтобы было легче ориентироваться.
        reply_markup=get_cancel_keyboard(),  # Добавляем клавиатуру отмены и возврата.
    )  # Завершаем отправку подсказки.


@router.callback_query(F.data == "cancel_breed_input")  # Обрабатываем кнопку отмены ввода породы.
async def cancel_breed_input_callback(callback: CallbackQuery, state: FSMContext) -> None:  # Создаём функцию отмены сценария поиска породы.
    await callback.answer("Ввод породы отменён.")  # Показываем короткое всплывающее уведомление пользователю.
    await state.clear()  # Полностью очищаем текущее состояние пользователя.
    await callback.message.answer("<b>✅ Режим ввода породы отключён.</b>", reply_markup=get_main_menu_keyboard())  # Возвращаем пользователя в главное меню.


@router.message(BreedForm.waiting_for_breed, F.text)  # Ловим обычный текст только тогда, когда бот ждёт название породы.
async def breed_input_handler(message: Message, state: FSMContext) -> None:  # Создаём функцию обработки введённого названия породы.
    breed_query = message.text.strip()  # Забираем текст пользователя и очищаем его от лишних пробелов.

    try:  # Начинаем безопасный блок работы с внешним API.
        await state.clear()  # Сразу очищаем состояние, чтобы после ответа диалог завершился.
        await send_breed_result(message, breed_query)  # Ищем породу и отправляем карточку результата.
    except Exception as error:  # Перехватываем возможные ошибки запроса.
        await message.answer(f"<b>⚠️ Не удалось обработать запрос.</b>\n{escape(str(error))}")  # Показываем понятную ошибку пользователю.