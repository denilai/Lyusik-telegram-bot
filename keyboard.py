from aiogram .types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

#row_markup = ReplyKeyboardMarkup(
#      resize_keyboard = True,  one_time_keyboard = True
#).add(button_first).add(button_second).add(button_third).add(button_fourth).add(button_fifth)


start_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton("Старт")).add(KeyboardButton("Конец"))
remove_markup=ReplyKeyboardRemove() 

#location_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeybardButton("i
