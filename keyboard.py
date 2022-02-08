from aiogram .types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_first = KeyboardButton ("Первый вариант")
button_second= KeyboardButton ("Haskell")
button_third= KeyboardButton ("Haskell")
button_fourth= KeyboardButton ("Четвертый вариант")
button_fifth= KeyboardButton ("Пятый вариант")
button_sixth= KeyboardButton ("Шестой вариант")

row_markup = ReplyKeyboardMarkup(
      resize_keyboard = True,  one_time_keyboard = True
).add(button_first).add(button_second).add(button_third).add(button_fourth).add(button_fifth)



haskell_markup = ReplyKeyboardMarkup(
      resize_keyboard = True,  one_time_keyboard = True
).add(KeyboardButton("Haskell")).add(KeyboardButton("Haskell")).add(KeyboardButton("Haskell"))


