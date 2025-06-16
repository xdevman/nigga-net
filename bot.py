#!/usr/bin/python

import threading
from time import sleep
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import os
from dotenv import load_dotenv
from database import *
from telebot.apihelper import ApiTelegramException
from config import *
load_dotenv()

# Read values from .env
TOKEN = os.getenv("TOKEN")
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() == "True"
PROXY = os.getenv("PROXY")

# Apply proxy if enabled
# if PROXY_ENABLED and PROXY:
#     apihelper.proxy = {"https": PROXY}

# Initialize bot
bot = telebot.TeleBot(TOKEN)

def is_sudo(m) -> bool:
    if m.from_user.id in sudo:
        return True
    return False

def is_user_joined(u) -> bool:
    result = bot.get_chat_member(JoinToChannel, u)
    if result.status != "left":
        return True
    return False

def get_join_markup():
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton(
        "✅[جوین شدم]",
        callback_data="check_join"
    )
    channel_button = types.InlineKeyboardButton(
        "🔗 جوین شدن به چنل",
        url=f"{channel_url}"
    )
    markup.add(channel_button)
    markup.add(join_button)
    return markup

# <<<<<<<<< ADMIN functions >>>>>>>>>>
@bot.message_handler(commands=["bc"], func=is_sudo)
def broadcast(m):
    try:
        M = m.reply_to_message
        if M:
            users = GET_users_id()
            print(users)
            if users:
                sent, faild = 0, 0
                bot.reply_to(m, "waiting...")
                for x in users:
                    print("userx",x)
                    try:
                        bot.copy_message(
                            x,
                            M.chat.id,
                            M.message_id,
                            M.caption,
                            None,
                            M.caption_entities,
                        )
                        sent += 1
                    except:
                        faild += 1
                bot.reply_to(
                    m, bc_style.format(
                        total=len(users), sent=sent, failed=faild)
                )
                return
        bot.reply_to(m, "something went wrong!!!")
    except Exception as e:
        bot.reply_to(m, f"broadcast: {e}")

# def is_user_joined(user_id):
#     try:
#         member = bot.get_chat_member(channel_id, user_id)
#         return member.status not in ["left", "kicked"]
#     except Exception as e:
#         print(f"Check join error: {e}")
#         return False


# <<<<<<<<< Commands >>>>>>>>>>
# start - help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    add_new_user(user_id)
    if not is_user_joined(user_id):
        bot.send_message(
            user_id,
            "🚫 : @CyberNigga2 برای استفاده از ربات باید توی چنل تلگرام جوین شین",
            reply_markup=get_join_markup()
        )
        return

    bot.reply_to(message, "Welcome! Use /link  to get your custom config")
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id

    if is_user_joined(user_id):
        bot.answer_callback_query(call.id, "✅ !اضافه شدید")
        bot.send_message(user_id, "برای گرفتن لینک از دستور /link استفاده کنید.")
        # Optional: You can re-run /start or another function here
    else:
        bot.answer_callback_query(call.id, "❌ هنوز به چنل اضافه نشدید")

# Start bot
bot.polling()