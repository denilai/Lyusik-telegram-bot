from loader import dp, bot, types
import commands 
import config
import re
#import sqlite3
import logging
import keyboard as kb
import database as db 
import states
from aiogram import executor, Dispatcher
import aiogram.utils.markdown as md
from typing import List, Awaitable, Union
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, sticker
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType



logging.basicConfig(level=logging.INFO)

#conn = sqlite3.connect('users.db')
#cur = conn.cursor()


#link to current asked question 
current_question_id : int = 1
right_answers_count : int = 0
visited_place : [str] = []


@dp.message_handler(content_types=types.ContentType.STICKER)
async def process_echo (message=types.Sticker):
  logging.info('this is that func {}'.format(message.content_type))
  await bot.send_sticker(config.MY_ID, r"CAACAgIAAxkBAAED-31iFBUGBMMNSD3Lf4h7aKtrLPE78gACoxAAAvF3qEh-OxgSw5fVQSME")
  await bot.send_sticker(config.MY_ID, message.sticker.file_id)


async def reset_vars():
  global current_question_id, right_answers_count, visited_place
  current_question_id=1
  right_answers_count=0 

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='конец', ignore_case=True), state='*')
async def process_cancel_cmd(message: types.Message, state: FSMContext):
  await reset_vars()
  global visited_place
  visited_place=[]
  current_state=await state.get_state()
  if current_state is None:
    return
  logging.info('Process /cancel command')
  logging.info('Current state is {}'.format(current_state))
  logging.info('Canceling state %r', current_state)
  await state.finish()
  await message.answer('Завершаем сеанс', reply_markup=kb.remove_markup)
 
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
  logging.info('Пользователь с именем {} начал приключение'.format(message.text))
  await state.update_data(username=message.text)
  await states.BotState.waiting_for_begin_of_quiz.set()
  await message.answer(md.text(
    md.text('Ааа, {}! Здравствуй!'.format(message.text)),
    #md.text(message.text),
    md.text('Я ждал твоего письма. Кирилл связался со мной.'),
    md.text('Ох и в историю он влип. Мафия, китайцы... Не хотелось ввязываться, но я обязан ему жизнью, буквально.'),
    md.text('Поэтому я помогу тебе в твоих поисках.'),
    md.text('Я уже имел дела с Крёстным отцом и знаю его методы. Он большой любитель квестов. Настолько большой, что даже дела ведет, будто все это один большой квест.'),
    md.text('Думаю, и в этот раз он приготовил что-то подобное.'), sep = '\n'))
  await message.answer(md.text(
    md.text('Я подключился к своему спутнику. Так, вижу тебя. Ты на даче. Хм, отличный дом!'),
    md.text('Еще вижу довольно странных людей неподалеку от тебя. Знакомая сигнатура... Может проверишь?'),sep='\n'))
  await message.answer(md.text(
    md.text('Такое ощущение, будто они специально там стоят, словно в видеоигре. Может у них и задание для нас найдется? Ха-ха-ха!'),
    md.text('Но все же нам не до смеха... Нам нужно найти сокровище, спрятaнное где-то неподалеку. И где же оно может быть?..'), sep='\n'))
  await message.answer(md.text(
    md.text('Крёстный отец хочет, чтобы мы играли по его правилам? Чтож, сыграем!'),
    md.text('Ты готова?!'),sep='\n'))
  await message.answer(md.text(
    md.text('Чтобы отправится в путь, нажми кнопку', md.bold('"Старт"'), '!'),
    md.text('Если ты не готова к приключению, нажми на кнопку',md.bold('"Конец"')),
    sep='\n'),reply_markup=kb.start_markup, parse_mode=ParseMode.MARKDOWN)



@dp.message_handler(state=states.BotState.waiting_for_begin_of_quiz)
async def correct_begining(message: types.Message, state: FSMContext):
  if message.text.upper() != 'СТАРТ': 
    logging.info('Пользователь ошибся с вводом. Ожидалось "СТАРТ", получили {}'.format(message.text))
    await message.reply('Чтобы отправится в путь, нажми кнопку "Старт"!\nЧтобы закончить приключение, нажми кнопку "Конец"',reply_markup = kb.start_markup)
    return
  await location_set(message, state)

async def location_set(message: types.Message, state:FSMContext):
  await message.answer("Помоги мне сориентироваться. Как называется место, где ты находишься? Я постараюсь узнать, что приготовил для нас Крёсный отец")
  await states.BotState.waiting_for_location.set()



async def first_setup(message: types.Message, state: FSMContext):
  user_data=await state.get_data()
  global current_question_id, right_answers_count
  await reset_vars()
  #await message.answer(question.media_list)
  await message.answer(md.text('{}, сейчас тебе предстоит ответить на вопросы от хозяев этой местности.'.format(user_data['username']),
    'Хитрить не выйдет. От  <b>Крёстного отца</b>, ничего не утаишь...','Удачи!', sep='\n'),parse_mode=types.ParseMode.HTML) 
  await ask_question(message, current_question_id, user_data['username'], message.from_user.id,user_data['location'])
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
    logging.info('Задан вопрос {} под номером {} в локации {}'.format(question.question, current_question_id, location))
  else:
    await message.answer('Нет вопросов для данной локации')
    logging.info('Обнаружен пустой вопрос в локации {} под номером {}'.format(location, current_question_id))



@dp.message_handler(state=states.BotState.waiting_for_location)
async def enter_location(message: types.Message, state: FSMContext):
  global visited_place
  diler_list = [r'[Дд]ил{1,2}ер', r'[Кк]ухня',r'[Нн]аркоман(ка)?',]
  chem_list = [r'[Хх]имики?',r'[Лл]аборатория']
  shtirliz_list = [r'[Шш]тирл[еи]ц',r'[Дд]етектив']
  mihal_list = [r'[Мм]ихалыч',r'[Мм]ихайлович', r'[Аа]вто', r'[Гг]араж']
  father_list = [r'[Кк]р[её]ст']
  if any(list(map(lambda y: y!=None,list(map(lambda x : re.search(x,message.text),diler_list))))):
    logging.info('first')
    logging.info('Активирована локация "Дилер"')
    logging.info('Проверяем список посещенных мест {}'.format(visited_place))
    if 'diler' in visited_place:
      await message.answer('Мы там уже были. Не стоит оглядываться назад)')
      return
    visited_place.append('diler')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='diler')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),chem_list))))):
    logging.info('second')
    logging.info('Активирована локация "Химики"')
    visited_place.append('chemist')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='chemist')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),shtirliz_list))))):
    logging.info('third')
    logging.info('Активирована локация "Штирлиц"')
    visited_place.append('shtirliz')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='shtirliz')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),mihal_list))))):
    logging.info('fouth')
    logging.info('Активирована локация "Автомастерская"')
    visited_place.append('garage')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='garage')
    await first_setup(message, state)
    return
  if any(list(map(lambda y: y!=None,list(map(lambda x :re.search(x,message.text),father_list))))):
    logging.info('fiveth')
    logging.info('Активирована локация "Крёстный отец"')
    visited_place.append('father')
    await states.BotState.waiting_for_end_of_quiz.set()
    await state.update_data(location='father')
    await first_setup(message, state)
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
    logging.info('Ошибочный ответ!')
  current_question_id+=1
  logging.info('После обработки сообщения: {}'.format(current_question_id))
  logging.info('Всего вопросов в данной секции: {}'.format(question.question_count))
  if current_question_id  > question.question_count:
    if right_answers_count >= 1+(question.question_count//2):
      await message.answer('Поздравляю, ты ответила на большинство вопросов. Крёстному отцу не добраться до нас!')
    else: 
      await message.answer('Охх, мы допустили слишком много ошибок. Теперь придется выполить задание Крёстного отца. Таков уговор...')
    await location_set(message, state)
    #await show_result(message, state)
    return
  await ask_question(message, current_question_id, user_data['username'], message.from_user.id,user_data['location'])


@dp.message_handler(lambda message: not message.text.__contains__('/'), state=states.BotState.show_result)
async def show_result(message: types.Message, state:FSMContext):
  user_data = await state.get_data()
  await message.answer("Ты ответила на все вопросы! Поздравляю, {}! Мы можем продолжить поиски сокровища!".format(user_data['username']),reply_markup=kb.remove_markup)
  logging.info('Локация {} успешно пройдена'.format(user_data['location']))
  await process_cancel_cmd(message, state)



if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
