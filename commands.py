from aiogram import types

from loader import dp, bot



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


