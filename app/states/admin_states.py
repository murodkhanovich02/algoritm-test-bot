from aiogram.fsm.state import State, StatesGroup


class CreateTestState(StatesGroup):
    waiting_for_pdf = State()
    waiting_for_test_code = State()
    waiting_for_time_limit = State()
    waiting_for_question_count = State()
    waiting_for_answer = State()


class AdminResultState(StatesGroup):
    waiting_for_test_code = State()


class ManageAdminState(StatesGroup):
    waiting_for_admin_id = State()
    waiting_for_delete_admin_id = State()