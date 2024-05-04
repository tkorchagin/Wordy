from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, AIORateLimiter, CommandHandler
import json
import config as co
import random

GUESSED_TEXT = "✅"
FAILED_TEXT = "❌"
REFRESH_TEXT = "🙈"
CHANGE_DICTIONARY_TEXT = "📚 Выбрать словарик"
START_TEXT = """
<b>Напиши мне, когда захочешь сыграть в Крокодила, Шляпу или Алиас ✨</b>

Как пользоваться @WordyBot:

1. Бот отправляет слово
2. Выбираешь, угадали ✅ или нет ❌
3. Жми 🙈 несколько раз, чтобы визуально отделить одну партию от другой

Считай галочки и крестики, чтобы подвести итоги.

Кстати, вот первое слово 👇
"""

# Load the data from the JSON file
with open('data.json') as file:
    data = json.load(file)

# Dictionary to store the current dictionary for each chat_id
current_dict_per_chat = {}

async def start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_TEXT, parse_mode='HTML')
    word = await get_random_word(update.effective_chat.id)
    await send_word(update.effective_chat.id, context.bot, word)

async def change_dictionary(update: Update, context):
    keyboard = [[InlineKeyboardButton(dictionary_name, callback_data=dictionary_name)] for dictionary_name in data.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📚 Выберите словарик:", reply_markup=reply_markup)

async def handle_callback_query(update: Update, context):
    query = update.callback_query
    current_dict_per_chat[query.message.chat_id] = query.data
    await query.edit_message_text(text=f"👌 Вы выбрали словарик: <b>{query.data}</b>", parse_mode="HTML")
    word = await get_random_word(query.message.chat_id)
    await send_word(query.message.chat_id, context.bot, word)

async def get_random_word(chat_id):
    current_dict = current_dict_per_chat.get(chat_id)
    if not current_dict:
        first_dict_name = list(data.keys())[0]
        current_dict_per_chat[chat_id] = first_dict_name
        current_dict = first_dict_name
    if current_dict and current_dict in data:
        word_list = data[current_dict]
        if word_list:
            random_word = random.choice(word_list)
            return random_word
    return "🙈 Хм, в этом словарике нет слов..."

async def send_word(chat_id, bot, word):
    keyboard = ReplyKeyboardMarkup([[GUESSED_TEXT, FAILED_TEXT], [REFRESH_TEXT], [CHANGE_DICTIONARY_TEXT]])
    await bot.send_message(chat_id=chat_id, text=word, reply_markup=keyboard)

async def handle_message(update: Update, context):
    text = update.message.text
    username = update.message.from_user.username
    user_id = update.message.chat_id
    print(f"User: {username} (ID: {user_id}), Message: {text}")
    
    if text.lower() == CHANGE_DICTIONARY_TEXT.lower():
        await change_dictionary(update, context)
    else:
        word = await get_random_word(update.effective_chat.id)
        await send_word(update.effective_chat.id, context.bot, word)

def main():
    print("Starting the bot...")
    application = (
        Application.builder()
        .token(co.TELEGRAM_BOT_TOKEN)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(None, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
