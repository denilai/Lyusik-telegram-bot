import config
import sqlite3
import logging

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

@dp.message_handler()
async def echo(message: types.Message):
  await message.answer(message.text)
  cur.execute('INSERT INTO USERS GUEST (2, "Dasha");')


if __name__ == "__main__":
  executor.start_polling(dp, skip_updates=True)
