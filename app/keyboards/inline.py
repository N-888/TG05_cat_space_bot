from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup  # Импортируем классы для создания красивых inline-кнопок.


def get_main_menu_keyboard() -> InlineKeyboardMarkup:  # Создаём функцию, которая собирает главное меню бота.
    return InlineKeyboardMarkup(  # Возвращаем готовую разметку inline-клавиатуры.
        inline_keyboard=[  # Передаём список строк с кнопками.
            [InlineKeyboardButton(text="🐱 Случайный котик", callback_data="cat_random")],  # Добавляем кнопку для случайной фотографии котика.
            [InlineKeyboardButton(text="🔎 Найти породу", callback_data="cat_breed")],  # Добавляем кнопку для поиска кошки по породе.
            [InlineKeyboardButton(text="🚀 Космос сегодня", callback_data="space_today")],  # Добавляем кнопку для космической картинки за сегодня.
            [InlineKeyboardButton(text="🌌 Случайный космос", callback_data="space_random")],  # Добавляем кнопку для случайной космической картинки.
            [InlineKeyboardButton(text="📅 Космос по дате", callback_data="space_date_help")],  # Добавляем кнопку-подсказку для запроса APOD по конкретной дате.
            [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="show_help")],  # Добавляем кнопку со справкой по возможностям бота.
        ]  # Завершаем список строк клавиатуры.
    )  # Завершаем создание клавиатуры.


def get_cancel_keyboard() -> InlineKeyboardMarkup:  # Создаём функцию для клавиатуры отмены ввода.
    return InlineKeyboardMarkup(  # Возвращаем готовую клавиатуру с одной строкой.
        inline_keyboard=[  # Передаём список строк с кнопками.
            [InlineKeyboardButton(text="❌ Отменить ввод", callback_data="cancel_breed_input")],  # Добавляем кнопку отмены режима ввода породы.
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="open_main_menu")],  # Добавляем кнопку быстрого возврата в главное меню.
        ]  # Завершаем список строк клавиатуры.
    )  # Завершаем создание клавиатуры.