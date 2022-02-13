import config
import sqlite3
import logging
import keyboard as kb
import database as db 

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)

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
dp = Dispatcher(bot)


question_counter = 1


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
  await message.answer('Привет! Введи свое имя')

@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)


@dp.message_handler()
async def answer(message: types.Message):
  global question_counter 
  #cur.execute("select * from (select row_number () over(order by id) row_num, * from guests ) where row_num = ?",(question_counter,))
  question=db.Question(question_counter)
  current_row = cur.fetchone()
  question_counter+=1
  await message.answer(question.question, reply_markup=question.variants_markup) 



if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
