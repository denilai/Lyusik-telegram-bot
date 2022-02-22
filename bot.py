import re
import config
import sqlite3
import logging
import keyboard as kb
import database as db 
import states
import aiogram.utils.markdown as md
from typing import List, Awaitable, Union
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, sticker
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType

AVATAR = 'AgACAgIAAxkDAAIGHWIKJFlRiW8SC8Dj_okcVKCfW0oLAAJyuDEb941QSHRliukKdqP5AQADAgADeAADIwQ'
VIDEO = 'BAACAgIAAxkDAAIHTWILX-Y4_wkzbRAp5-6XsfU-ivC9AAITFQACJRRZSFKSAxWmOKXOIwQ'


logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('users.db')
cur = conn.cursor()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

#link to current asked question 
current_question_id : int = 1
right_answers_count : int = 0



@dp.message_handler(content_types=types.ContentType.STICKER)
async def process_echo (message=types.Sticker):
  logging.info('this is that func {}'.format(message.content_type))
  await bot.send_sticker(config.MY_ID, r"CAACAgIAAxkBAAED-31iFBUGBMMNSD3Lf4h7aKtrLPE78gACoxAAAvF3qEh-OxgSw5fVQSME")
  await bot.send_sticker(config.MY_ID, message.sticker.file_id)

@dp.message_handler(commands='photo', state='*')
async def process_photo_cmd (message: types.Message, state:FSMContext):
  caption = 'Вот аватар бота! :red_heart:'
  await bot.send_photo(message.from_user.id,AVATAR, caption=emojize(caption), reply_to_message_id=message.message_id) 
  logging.info('Process /photo command')

@dp.message_handler(commands='video', state='*')
async def process_video_cmd (message: types.Message):
  caption = 'Вот тебе видосик :red_heart:'
  await bot.send_video(message.from_user.id, VIDEO, caption = emojize(caption), reply_to_message_id=message.message_id)
  logging.info('Process /video command')


@dp.message_handler(commands='start', state='*')
#@dp.message_handler(state=None)
async def process_start_cmd(message : types.Message, state=FSMContext):
  await process_help_cmd(message)
  await message.answer('Привет! Введи свое имя', reply_markup=kb.remove_markup)
  await states.BotState.waiting_for_name.set()
  logging.info('Message chat id = {}'.format(message.chat.id))
  logging.info('Process /start command')

@dp.message_handler(commands='help', state='*')
async def process_help_cmd(message: types.Message):
  await message.answer(md.text(
    'Я Люсик! Бот, который проводит викторины, часть моего функционала сейчас в разработке.',
    'Мне очень приятно поболтать с тобой!',
    'Вот, что я умею:',
    '/help - вывести эту справку',
    '/start - начать виктронину',
    '/video - отправить тестовое видео',
    '/photo - отправить тестовое фото',
    '/cancel - закончить викторину',sep='\n'))
  logging.info('Process /help command')


async def reset_vars():
  global current_question_id, right_answers_count
  current_question_id=1
  right_answers_count=0 

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='конец', ignore_case=True), state='*')
async def process_cancel_cmd(message: types.Message, state: FSMContext):
  await reset_vars()
  current_state=await state.get_state()
  if current_state is None:
    return
  logging.info('Canceling state %r', current_state)
  await state.finish()
  logging.info('Current state is {}'.format(current_state))
  await message.answer('Завершаем сеанс', reply_markup=kb.remove_markup)
  logging.info('Process /cancel command')
 
#@dp.message_handler(state='*')
##@dp.message_handler(commands=['myCommand'], commands_prefix='!/')
#async def default (message : types.Message):
#  await message.reply('Прости, мой искусственный интелект не идеален, может попробуем еще раз?')

@dp.message_handler(lambda message: not message.text.__contains__('/'), state=states.BotState.waiting_for_name)
async def greeting(message: types.Message, state = FSMContext):
  #if message.text.__contains__('/'):
  #    await message.answer('Имя не может содержать символа "/". Попробуешь еще раз?')
  #    return 
  db.UserMaster.add_user(message.text)
  await state.update_data(username=message.text)
  await states.BotState.waiting_for_begin_of_quiz.set()
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
async def correct_begining(message: types.Message, state: FSMContext):
  if message.text.upper() != 'СТАРТ': 
    await message.reply('Чтобы начать викторину, нажми "Старт"\nЧтобы закончить сеанс, нажми "Конец"',reply_markup = kb.start_markup)
    return
  await location_set(message, state)

async def location_set(message: types.Message, state:FSMContext):
  await message.answer("Введи название локации")
  await states.BotState.waiting_for_location.set()



async def first_setup(message: types.Message, state: FSMContext):
  user_data=await state.get_data()
  global current_question_id, right_answers_count
  await reset_vars()
  await ask_question(message, current_question_id, user_data['username'], message.from_user.id,user_data['location'])
  #await message.answer(question.media_list)
  await message.answer(md.text('{}, сейчас тебе предстоит ответить на вопросы от хозяина локации.'.format(user_data['username']),
                               'Будь внимательна! Нужно овтетить на большинство вопросов, иначе тебе предстоит выполнить задание.',
                               'От  <b>Крёстного отца</b>, ничего не утаишь...','Удачи!', sep='\n'),parse_mode=types.ParseMode.HTML) 
  logging.info('first setup with location = {} and message = {}'.format(user_data['location'], message.text))

async def ask_question(message, current_question_id, username, user_id, location):
  question= db.QuestionMaster(current_question_id, username, user_id, location)
  if question.media_list==[]:
    logging.info('Нет вложений')
  else:
    for record in question.media_list:
      if record[0]=='photo':
        await bot.send_photo(message.from_user.id, record[1]) 
      if record[0]=='video':
        await bot.send_video(message.from_user.id, record[1])
      if record[0]=='file':
        await bot.send_file(message.from_user.id, record[1])
  if question.question!="": 
    await message.answer(question.question, reply_markup=question.variants_markup) 
  else:
    await message.answer('Нет вопросов для данной локации')



@dp.message_handler(state=states.BotState.waiting_for_location)
async def enter_location(message: types.Message, state: FSMContext):
  diller_list = [r'.ил{1,2}ер', r'.ухня',r'[Нн]аркоман(ка)?',]
  chem_list = [r'[Хх]имики?',r'[Лл]аборатория']
  shtirlez_list = [r'[Шш]тирлец',r'[Дд]етектив']
  mihal_list = [r'[Мм]ихалыч',r'[Мм]ихайлович']
  if any(list(map(lambda y: y!=None,list(map(lambda x : re.search(x,message.text),diller_list))))):
    logging.info('first')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='diller')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),chem_list))))):
    logging.info('second')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='chemist')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),shtirlez_list))))):
    logging.info('third')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='shtirlez')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),mihal_list))))):
    logging.info('fouth')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='mihalych')
    logging.info('Не прописан вариант с Михалычем')
    #await first_setup(message, state)
    return
  await message.answer('Извини, не нашел такой локации. Введи еще раз')



#@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
#async def begin_quiz(message: types.Message, state:FSMContext):
#  global current_question_id
#  if message.text.upper() != 'СТАРТ': 
#    await message.reply('Чтобы начать викторину, нажми "Старт"\nЧтобы закончить сеанс, нажми "Конец"',reply_markup = kb.start_markup)
#    return
#  await states.BotState.next()
#  await message.answer('Поехали!!!')
#  user_data=await state.get_data()
#  question= db.QuestionMaster(current_question_id, user_data['username'], message.from_user.id, 'diller')
#  await message.answer(question.media_list)
#  await message.answer(question.question, reply_markup=question.variants_markup) 
#  #await state.update_data(current_question_id=current_question_id+1)

#@dpquestion..message_handler(state=states.BotState.waiting_for_begin_of_quiz)
#async def wrong_cmd(message: types.Message, state:FSMContext):
# await(message.answer(  

@dp.message_handler(lambda message: not message.text.__contains__('/'),state=states.BotState.waiting_for_end_of_quiz)
async def quiz(message: types.Message, state: FSMContext):
  global current_question_id, right_answers_count
  user_data=await state.get_data()
  question= db.QuestionMaster(current_question_id, user_data['username'], message.from_user.id,user_data['location'])
  logging.info('Current question counter = {}'.format(current_question_id))
  logging.info('---\nСравниваем '+message.text.upper()+' '+ question.right_answer.upper())
  logging.info('До обработки сообщения: {}'.format(current_question_id))
  question.set_user_answer(message.text)
  #question.set_username(user_data['username'])
  question.log()
  if question.user_is_right:
    await message.reply('Верно!')
    right_answers_count=right_answers_count+1
    logging.info('Текущее количество правильных ответов = {}'.format(right_answers_count))
  else:
    await message.reply('В этот раз не повезло((') #Придется выполнить наказание от Крёстного отца')
  current_question_id+=1
  logging.info('После обработки сообщения: {}'.format(current_question_id))
  logging.info('Всего вопросов в данной секции: {}'.format(question.question_count))
  if current_question_id  > question.question_count:
    if right_answers_count >= 1+(question.question_count//2):
      await message.answer('Поздравляю, ты ответила на большинство вопросов. Крестному отцу не добраться до нас!')
    else: 
      await message.answer('Охх, мы допустили слишком много ошибок. Теперь придется выполить задание Крёстного отца. Таков уговор...')
    await location_set(message, state)
    #await show_result(message, state)
    return
  await ask_question(message, current_question_id, user_data['username'], message.from_user.id,user_data['location'])


@dp.message_handler(lambda message: not message.text.__contains__('/'), state=states.BotState.show_result)
async def show_result(message: types.Message, state:FSMContext):
  user_data = await state.get_data()
  await message.answer("Ты ответила на все вопросы! Поздравляю, {}!".format(user_data['username']),reply_markup=kb.remove_markup)
  await process_cancel_cmd(message, state)




if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
