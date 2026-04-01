from aiogram import Router  # Импортируем тип Router, чтобы точно указать тип возвращаемых объектов.

from .cats import router as cats_router  # Импортируем роутер с кошачьими командами.
from .common import router as common_router  # Импортируем роутер с общими командами и подсказками.
from .space import router as space_router  # Импортируем роутер с космическими командами.


def get_routers() -> tuple[Router, ...]:  # Создаём функцию, которая отдаёт все роутеры проекта в нужном порядке.
    return cats_router, space_router, common_router  # Возвращаем роутеры так, чтобы общий текстовый обработчик сработал самым последним.