import config
import sqlite3
import logging
import keyboard as kb
import database as db 
import states
import aiogram.utils.markdown as md
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

AVATAR = 'AgACAgIAAxkDAAIGHWIKJFlRiW8SC8Dj_okcVKCfW0oLAAJyuDEb941QSHRliukKdqP5AQADAgADeAADIwQ'

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('users.db')
cur = conn.cursor()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

#link to current asked question 
current_question_id : int = 1

#@dp.message_handler()
#async def process_echo (message= types.Message):
#  logging.info(message.text)
#  await message.answer(message.text)

@dp.message_handler(commands='photo')
#@dp.message_handler(state='*')
async def process_photo_cmd (message: types.Message, state:FSMContext):
  caption = 'Вот аватар бота! :red_heart:'
  await bot.send_photo(message.from_user.id,AVATAR, caption=emojize(caption), reply_to_message_id=message.message_id) 



@dp.message_handler(commands=['start'])
@dp.message_handler(state=None)
async def cmd_start(message : types.Message, state=FSMContext):
  await message.answer('Привет! Введи свое имя', reply_markup=kb.remove_markup)
  await states.BotState.waiting_for_name.set()
  logging.info(message.chat.id)


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
  await message.answer('Завершаем сеанс', reply_markup=kb.remove_markup)
 

@dp.message_handler(state=states.BotState.waiting_for_name)
async def greeting(message: types.Message, state = FSMContext):
  if message.text.__contains__('/'):
      await message.answer('Имя не может содержать символа "/". Попробуешь еще раз?')
      return 
  await state.update_data(username=message.text)
  await states.BotState.next()
  await message.answer(md.text(
    md.text('Привет,',message.text+'!'), 
    md.text('Тебя ждет приятный сюрприз!'),
    md.text('Тебе предстоит пройти викторину, в которую будут входить вопросы от твоих гостей!'),
    md.text('Чтобы начать викторину, нажми кнопку', md.bold('"Старт"'), '!'),
    md.text('Чтобы завершить общение со мной, нажми на кнопку',md.bold('"Конец"')),
    sep='\n'
  ),reply_markup=kb.start_markup, parse_mode=ParseMode.MARKDOWN)
  await message.answer('{}, чтобы начать викторину, нажми "Старт")'.format(message.text),reply_markup = kb.start_markup)


@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
async def begin_quiz(message: types.Message, state:FSMContext):
  global current_question_id
  if message.text.upper() != 'СТАРТ': 
    await message.reply('Чтобы начать викторину, нажми "Старт"\nЧтобы закончить сеанс, нажми "Конец"',reply_markup = kb.start_markup)
    return
  await states.BotState.next()
  await message.answer('Поехали!!!')
  question= db.Question(current_question_id)
  await message.answer(question.media_list)
  await message.answer(question.question, reply_markup=question.variants_markup) 
  #await state.update_data(current_question_id=current_question_id+1)

#@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
#async def wrong_cmd(message: types.Message, state:FSMContext):
# await(message.answer(  

@dp.message_handler(state=states.BotState.waiting_for_end_of_quiz)
async def quiz(message: types.Message, state: FSMContext):
  global current_question_id
  question= db.Question(current_question_id)
  logging.info('---\nСравниваем '+message.text.upper()+' '+ question.right_answer.upper())
  logging.info('До обработки сообщения: {}'.format(current_question_id))
  if message.text.upper()==question.right_answer.upper():
    await message.reply('Верно!')
    if current_question_id  >= question.question_count:
      await states.BotState.show_result.set()
      await show_result(message, state)
      return
    current_question_id+=1
  else:
    await message.reply('В этот раз не повезло( Попробуем еще?')
  logging.info('После обработки сообщения: {}'.format(current_question_id))
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

@dp.message_handler(state='*')
async def default (message : types.Message):
  await message.reply('Прости, мой искусственный интелект не идеален, может попробуем еще раз?')


if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
