import config
import sqlite3
import logging
import keyboard as kb

from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('SELECT * FROM GUEST;')
record = cur.fetchall()
print("Версия базы данных SQLite: ", record)
sqlite_select_query = "select sqlite_version();"
cur.execute(sqlite_select_query)
record = cur.fetchall()
print("Версия базы данных SQLite: ", record)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
  await message.answer('Привет. Самый важный вопрос в жизни. Какой язык программирования самый лучший?', reply_markup=kb.haskell_markup)


@dp.message_handler()
async def echo(message: types.Message):
  await message.answer(message.text, reply_markup=kb.row_markup)
  cur.execute('INSERT INTO GUEST values (2, "Dasha");')


if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
