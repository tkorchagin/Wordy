import telebot
import json
import time
from telebot import types
import config as co
import random


GUESSED_TEXT = "✅"
FAILED_TEXT = "❌"
REFRESH_TEXT = "🙈"
CHANGE_DICTIONARY_TEXT = "📚 Change Dictionary"
START_TEXT = """
<b>Напиши мне, когда захочешь сыграть в Крокодила, Шляпу или Алиас ✨</b>

Как пользоваться @WordyBot:

1. Бот отправляет слово
2. Выбираешь, угадали ✅ или нет ❌
3. Жми 🙈 несколько раз, чтобы визуально отделить одну партию от другой

Считай галочки и крестики, чтобы подвести итоги.

Кстати, вот первое слово 👇
"""

bot = telebot.TeleBot(co.TELEGRAM_BOT_TOKEN)

# Load the data from the JSON file
with open('data.json') as file:
    data = json.load(file)

# Store the current dictionary name
current_dict = list(data.keys())[0]  # Select the first dictionary

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, START_TEXT, parse_mode='HTML')
    send_word(message.chat.id)

@bot.message_handler(func=lambda message: message.text.lower() == CHANGE_DICTIONARY_TEXT.lower())
def handle_change_dictionary(message):
    keyboard = types.InlineKeyboardMarkup()
    for dictionary_name in data.keys():
        button = types.InlineKeyboardButton(dictionary_name, callback_data=dictionary_name)
        keyboard.add(button)
    bot.send_message(message.chat.id, "📚 Select a dictionary:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global current_dict
    current_dict = call.data
    bot.send_message(call.message.chat.id, f"👌 You selected the dictionary '{current_dict}'")
    send_word(call.message.chat.id)

def get_random_word():
    if current_dict in data:
        word_list = data[current_dict]
        if word_list:
            random_word = random.choice(word_list)
            return random_word
    return "🙈 No words available in the current dictionary."

def send_word(chat_id):
    word = get_random_word()
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton(GUESSED_TEXT), types.KeyboardButton(FAILED_TEXT))
    keyboard.add(types.KeyboardButton(REFRESH_TEXT))
    keyboard.add(types.KeyboardButton(CHANGE_DICTIONARY_TEXT))
    bot.send_message(chat_id, word, reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    send_word(message.chat.id)

if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            time.sleep(5)
