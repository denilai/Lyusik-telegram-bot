from aiogram import types
from loader import dp, bot
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
import logging
import states
import keyboard as kb
import config

AVATAR = 'AgACAgIAAxkDAAIGHWIKJFlRiW9SC8Dj_okcVKCfW0oLAAJyuDEb941QSHRliukKdqP5AQADAgADeAADIwQ'
VIDEO = 'BAACAgIAAxkDAAIHTWILX-Y4_wkzbRAp5-6XsfU-ivC9AAITFQACJRRZSFKSAxWmOKXOIwQ'

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
  #await process_help_cmd(message)
  await message.answer('Откуда у вас моя визитка? А, вижу, у вас ко мне дело. Мы встречались раньше? Назовитесь, будьте любезны.', reply_markup=kb.remove_markup)
  await states.BotState.waiting_for_name.set()
  logging.info('Message chat id = {}'.format(message.chat.id))
  logging.info('Process /start command')

@dp.message_handler(commands='help', state='*')
async def process_help_cmd(message: types.Message):
  await message.answer(md.text(
    'Я Микки Кувыркун, частный детектив. Я вызвался помочь найти своего друга Кирилла, спасти его из лап Чертановской мафии.',
    'Вот, что я умею:',
    '/help - вывести эту справку',
    '/start - начать виктронину',
    '/video - отправить видео',
    '/photo - отправить фото',
    '/cancel - закончить приключение ',sep='\n'))
  logging.info('Process /help command')


