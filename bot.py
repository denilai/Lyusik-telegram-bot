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

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

#link to current asked question 
current_question_id = 1

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
    md.text('Тебя ждет приятный сюрприз!'),
    md.text('Тебе предстоит пройти викторину, в которую будут входить вопросы от твоих гостей. Будь внимательна!'),
    md.text('Чтобы начать виктрорину, нажми кнопку', md.bold('"Старт"'), '!'),
    md.text('Чтобы завершить общение со мной, нажми на кнопку',md.bold('"Конец"')),
    sep='\n'
  ),reply_markup=kb.start_markup, parse_mode=ParseMode.MARKDOWN)
  await message.answer('{}, чтобы начать викторину, введи "Старт")'.format(message.text),reply_markup = kb.start_markup)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='конец', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
  global current_question_id
  current_question_id=1
  current_state=await state.get_state()
  if current_state is None:
    return

  logging.info('Canceling state %r', current_state)
  await state.finish()
  await message.reply('Завершаем сеанс', reply_markup=kb.remove_markup)


@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
async def begin_quiz(message: types.Message, state:FSMContext):
  global current_question_id
  if message.text.upper() != 'СТАРТ': 
    await message.reply('Чтобы начать викторину, нажми "Старт")',reply_markup = kb.start_markup)
    return
  await states.BotState.next()
  await message.answer('Поехали!!!')
  question= db.Question(current_question_id)
  await message.answer(question.question, reply_markup=question.variants_markup) 
  #await state.update_data(current_question_id=current_question_id+1)

#@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
#async def wrong_cmd(message: types.Message, state:FSMContext):
# await(message.answer(  

@dp.message_handler(state=states.BotState.waiting_for_end_of_quiz)
async def answer(message: types.Message, state: FSMContext):
  user_data = await state.get_data()
  global current_question_id
  question= db.Question(current_question_id)
  logging.info('Сравниваем '+message.text.upper()+' '+ question.right_answer.upper())
  logging.info('До обработки сообщенияi: ', current_question_id)
  if message.text.upper()==question.right_answer.upper():
    await message.reply('Верно!')
    if current_question_id  >= question.question_count:
      states.BotState.show_result.set()
      await show_result(message, state)
      return
    current_question_id+=1
  else:
    await message.reply('В этот раз не повезло( Попробуем еще?')
  logging.info('После обработки сообщения: ',current_question_id)
  next_question= db.Question(current_question_id)
  await message.answer(next_question.question, reply_markup=next_question.variants_markup) 


@dp.message_handler(state=states.BotState.show_result)
async def show_result(message: types.Message, state:FSMContext):
  user_data = await state.get_data()
  await message.answer("Ты ответила на все вопросы! Поздравляю, {}!".format(user_data['username']),reply_markup=kb.remove_markup)
  await cancel_handler(message, state)

@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)

if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
