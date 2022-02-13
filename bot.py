import config
import sqlite3
import logging
import keyboard as kb
import database as db 
import states
import aiogram.utils.markdown as md
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.DEBUG)

conn = sqlite3.connect('users.db')
cur = conn.cursor()
#cur.execute('SELECT * FROM GUEST;')
#record = cur.fetchall()
#print("Версия базы данных SQLite: ", record)
#sqlite_select_query = "select sqlite_version();"
#cur.execute(sqlite_select_query)
#record = cur.fetchall()
#print("Версия базы данных SQLite: ", record)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

question_counter = 1

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
  await message.answer('Привет! Введи свое имя')
  await states.BotState.waiting_for_name.set()

@dp.message_handler(state=states.BotState.waiting_for_name)
async def greeting(message: types.Message, state = FSMContext):
  await state.update_data(username=message.text.lower())
  await states.BotState.next()
  await message.answer(md.text(
    md.text('Привет,',message.text+'!'), 
    md.text('Сейчас тебя будет ждать приятный сюрприз!'),
    md.text('Тебе предстоит пройти викторину, в которую будут входить вопросы от твоих гостей. Будь внимательна!'),
    md.text('Чтобы начать виктрорину, нажми кнопку', md.bold('"Старт"'), '!'),
    md.text('Чтобы завершить общение со мной, введи',md.bold('"/cancel"')),
    sep='\n'
  ),reply_markup=kb.start_markup, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='конец', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
  current_state=await state.get_state()
  if current_state is None:
    return

  logging.info('Canceling state %r', current_state)
  await state.finish()
  await message.reply('Завершаем сеанс', reply_markup=kb.remove_markup)


@dp.message_handler(Text(equals='Старт', ignore_case=True), state=states.BotState.waiting_for_begin_of_quiz)
async def begin_quiz(message: types.Message, state:FSMContext):
  global question_counter
  await states.BotState.next()
  await message.answer('Поехали!!!')
  question= db.Question(question_counter)
  await message.answer(question.question, reply_markup=question.variants_markup) 
  #await state.update_data(question_counter=question_counter+1)

@dp.message_handler(state=states.BotState.waiting_for_end_of_quiz)
async def answer(message: types.Message, state: FSMContext):
  global question_counter
  question= db.Question(question_counter)
  #previous_question= db.Question(question_counter-1)
  logging.info('Сравниваем '+message.text.upper()+' '+ question.right_answer.upper())
  logging.info(question_counter)
  if message.text.upper()==question.right_answer.upper():
    await message.reply('Верно!')
    question_counter+=1
    logging.info(question_counter)
  else:
    await message.reply('В этот раз не повезло..(')
  logging.info(question_counter)
  next_question= db.Question(question_counter)
  await message.answer(next_question.question, reply_markup=next_question.variants_markup) 


@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)

if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
