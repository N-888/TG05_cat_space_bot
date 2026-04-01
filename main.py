# Импортируем asyncio, чтобы запускать асинхронную функцию main.
import asyncio

# Импортируем logging, чтобы видеть понятные сообщения о запуске и ошибках в консоли.
import logging

# Импортируем классы Bot и Dispatcher из aiogram.
from aiogram import Bot, Dispatcher

# Импортируем настройки бота по умолчанию.
from aiogram.client.default import DefaultBotProperties

# Импортируем режим HTML для красивого форматирования сообщений.
from aiogram.enums import ParseMode

# Импортируем сетевую ошибку Telegram из aiogram.
from aiogram.exceptions import TelegramNetworkError

# Импортируем функцию чтения настроек из файла .env.
from app.config import get_config

# Импортируем функцию, которая подключает все роутеры проекта.
from app.handlers import get_routers


# Создаём главную асинхронную функцию запуска проекта.
async def main() -> None:
    # Включаем логи с датой, уровнем и текстом сообщения.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Загружаем токены и ключи из файла .env.
    config = get_config()

    # Открываем бота через async with, чтобы сессия закрывалась корректно даже при ошибке.
    async with Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    ) as bot:
        # Создаём диспетчер.
        dp = Dispatcher()

        # Подключаем все роутеры проекта.
        for router in get_routers():
            # Добавляем текущий роутер в диспетчер.
            dp.include_router(router)

        try:
            # Проверяем, может ли бот вообще достучаться до Telegram API.
            me = await bot.get_me(request_timeout=60)

            # Пишем в лог, что подключение к Telegram успешно.
            logging.info("Подключение к Telegram успешно: @%s", me.username)

        except TelegramNetworkError as error:
            # Останавливаем запуск с понятным текстом, если Telegram API недоступен.
            raise RuntimeError(
                "Не удалось подключиться к Telegram API.\n"
                "Проверьте интернет, VPN/прокси, антивирус, фаервол и доступ к api.telegram.org."
            ) from error

        try:
            # Пытаемся удалить webhook и очистить старые обновления перед polling.
            await bot.delete_webhook(drop_pending_updates=True, request_timeout=60)

            # Пишем в лог, что webhook успешно удалён.
            logging.info("Webhook успешно удалён.")

        except TelegramNetworkError:
            # Не падаем сразу, а просто предупреждаем в логе.
            logging.warning("Не удалось удалить webhook. Продолжаем запуск.")

        # Запускаем long polling.
        await dp.start_polling(bot, polling_timeout=30)


# Проверяем, что файл запущен напрямую.
if __name__ == "__main__":
    try:
        # Запускаем асинхронную функцию main.
        asyncio.run(main())

    except KeyboardInterrupt:
        # Печатаем понятное сообщение при ручной остановке.
        print("Бот остановлен пользователем.")

    except RuntimeError as error:
        # Печатаем понятную ошибку сети к Telegram.
        print(error)