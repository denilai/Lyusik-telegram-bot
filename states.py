from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class BotState (StatesGroup):
  #initial = State()
  waiting_for_name = State()
  waiting_for_begin_of_quiz = State()
  waiting_for_location = State()
  waiting_for_end_of_quiz = State()
  show_result = State()
 
