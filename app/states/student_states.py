from aiogram.fsm.state import State, StatesGroup


class StudentTestState(StatesGroup):
    waiting_for_test_code = State()
    waiting_for_full_name = State()
    waiting_for_answer = State()