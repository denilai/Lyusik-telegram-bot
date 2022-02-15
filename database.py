import sqlite3, datetime
from aiogram .types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton
import logging
logging.basicConfig(level=logging.INFO)
conn = sqlite3.connect('users.db')
cur = conn.cursor()

class QuestionMaster:
  def __init__ (self, id, username, user_id):
    self.user_id=user_id
    self.username = username
    cur.execute('select question_text, right_answer from questions where question_id = ?',(id,))
    quest_record = cur.fetchone()
    self.question = quest_record[0]
    self.right_answer = quest_record[1]
    cur.execute('select * from (select answer_text a from wrong_answers where question_id = ? union select right_answer from questions where question_id = ?) order by a', (id,id))
    self.wrong_answers = cur.fetchall()
    self.variants_markup= ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for answer in self.wrong_answers:
      self.variants_markup.add(KeyboardButton(answer[0]))
    self
    cur.execute('select count(distinct question_id) from questions')
    self.question_count = cur.fetchone()[0] 
    cur.execute('select media_type, filename from question_media where question_id = ?',(id,))
    media_record = cur.fetchall()
    self.media_list = []
    for row in media_record:
      self.media_list.append((row[2],))
    self.user_answer=""
    self.user_is_right=False
    
  def set_user_answer(self, user_answer):
    self.user_answer = user_answer
    self.user_is_right = self.user_answer.upper()==self.right_answer.upper()

  def log(self):
    cur.execute('insert into log (timestamp, user_id,  user, question, answer, is_right) values (?,?,?,?,?,?)', (datetime.datetime.now(), self.user_id, self.username, self.question, self.user_answer, self.user_is_right))
    conn.commit()


class UserMaster:
  @staticmethod
  def add_user(username):
    cur.execute('select count(name) from users where name= ?',(username,))
    name_record = cur.fetchone()
    logging.info(name_record)
    if name_record[0]==0: 
      cur.execute('insert into users (name) values (?)',(username,))
      conn.commit()
