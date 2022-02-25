import sqlite3, datetime
from aiogram .types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import logging
logging.basicConfig(level=logging.INFO)
conn = sqlite3.connect('users.db')
cur = conn.cursor()

class QuestionMaster:
  def __init__ (self, current_id, username, user_id, location):
    logging.info('Обрабатываем вопрос \ncurrent_id = {}\nusername = {}\nuser_id = {}\n location = {}'.format(current_id, username, user_id, location))
    self.id = current_id
    self.user_id=user_id
    self.username = username
    self.location = location
    self.user_answer=""
    self.user_is_right=False
    self.variants_markup= ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    self.media_list = []
    self.media_answer_list = []
    self.question=""
    self.right_answer=""
    self.question_id = 0
    self.question_count = 0

    self.set_question_parameters()
    self.set_media_list()


  def set_question_parameters(self):
    cur.execute('select question_text, right_answer, question_id '+
                'from ('+
                'select row_number() over(order by question_id) rn, * from questions where location = ?) '+
                'where rn = ?',(self.location,self.id))
    quest_record = cur.fetchone()
    logging.info('Запросы по данной локации {}'.format(quest_record))
    if quest_record!=[] and quest_record != None:
      self.question = quest_record[0]
      self.right_answer = quest_record[1]
      self.question_id = quest_record[2]

    cur.execute('select * from ('+
                'select answer_text a from wrong_answers where question_id = ? union '+
                'select right_answer from questions where question_id = ?) '+'order by a', (self.question_id,self.question_id))
    self.answers = cur.fetchall()
    if self.answers != [] and self.answers != None:  
      for answer in self.answers:
        self.variants_markup.add(KeyboardButton(answer[0]))

    cur.execute('select count(distinct question_id) from questions where location = ?',(self.location,))
    question_count_rec = cur.fetchone() 
    if question_count_rec !=[] and question_count_rec != None:
      self.question_count = question_count_rec[0]


  def set_media_list(self):
    cur.execute('select media_type, ids.file_id from question_media q join media_ids ids on  upper(q.filename)=upper(ids.filename)  where question_id = ?' ,(self.question_id,))
    media_record = cur.fetchall()
    logging.info('Медия файлы вопроса - {}'.format(media_record))
    if media_record != None and media_record != []:
      for row in media_record:
        self.media_list.append((row[0],row[1]))

    cur.execute('select media_type, ids.file_id from answer_media q join media_ids ids on  upper(q.filename)=upper(ids.filename)  where question_id = ?' ,(self.question_id,))
    media_record = cur.fetchall()
    logging.info('Медия файлы ответа - {}'.format(media_record))
    if media_record != None and media_record != []:
      for row in media_record:
        self.media_answer_list.append((row[0],row[1]))
    
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
