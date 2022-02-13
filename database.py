import sqlite3
from aiogram .types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton
import logging
logging.basicConfig(level=logging.INFO)
conn = sqlite3.connect('users.db')
cur = conn.cursor()

class Question:
  def __init__ (self, id):
    cur.execute('select question_text, right_answer from questions where question_id = ?',(id,))
    quest_record = cur.fetchone()
    self.question = quest_record[0]
    self.right_answer = quest_record[1]
    cur.execute('select answer_text from wrong_answers where question_id = ?', (id,))
    self.wrong_answers = cur.fetchall()
    self.variants_markup= ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for answer in self.wrong_answers:
      self.variants_markup.add(KeyboardButton(answer[0]))

