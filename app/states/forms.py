from aiogram.fsm.state import State, StatesGroup  # Импортируем базовые классы состояний для пошагового диалога.


class BreedForm(StatesGroup):  # Создаём группу состояний для сценария поиска породы.
    waiting_for_breed = State()  # Описываем состояние, в котором бот ждёт название породы от пользователя.