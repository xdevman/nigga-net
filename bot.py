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
from Panel_client import *
load_dotenv()

# Read values from .env
TOKEN = os.getenv("TOKEN")
# PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() == "True"
# PROXY = os.getenv("PROXY")

# Apply proxy if enabled
# if PROXY_ENABLED and PROXY:
telebot.apihelper.proxy = {'https': 'socks5h://127.0.0.1:2080'}

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
@bot.message_handler(commands=["reset"], func=is_sudo)
def reset_traffic(m):
    try:
        users = GET_users_id()
        if users:
            bot.reply_to(m, "waiting...")
            try:
                result = PanelClient.reset_users(users)
                sent += 1
            except:
                faild += 1
            bot.reply_to(m,result)
        
    except Exception as e:
        bot.reply_to(m, f"broadcast: {e}")
@bot.message_handler(commands=["bc"], func=is_sudo)
def broadcast(m):
    try:
        M = m.reply_to_message
        if M:
            users = GET_users_id()
            # print(users)
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
        bot.reply_to(m, f"reset: {e}")

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

    bot.reply_to(message, "برای گرفتن لینک از دستور /link استفاده کنید.")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id

    if is_user_joined(user_id):
        bot.answer_callback_query(call.id, "✅ !اضافه شدید")
        bot.send_message(user_id, "برای گرفتن لینک از دستور /link استفاده کنید.")
        # Optional: You can re-run /start or another function here
    else:
        bot.answer_callback_query(call.id, "❌ هنوز به چنل اضافه نشدید")

@bot.message_handler(commands=['link'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_user_joined(user_id):
        bot.send_message(
            user_id,
            "🚫 : @CyberNigga2 برای استفاده از ربات باید توی چنل تلگرام جوین شین",
            reply_markup=get_join_markup()
        )
        return
    is_link_generated = link_status(user_id)
    if is_link_generated[0][0] == True:
        res = client_xui.get_user(str(user_id))
        bot.reply_to(message, f"```{res}```", parse_mode='MarkdownV2')
    else:
        result = client_xui.add_ss_client(str(user_id))
        if result["success"]:
            #  set link status : true on DB
            update_linkStatus(user_id)
            bot.reply_to(message, f'```{result["link"]}```',parse_mode='MarkdownV2')
        else:
          bot.reply_to(message, "Error: Try Again")



# Start bot
client_xui = PanelClient(PANEL_URL, PANEL_USER, PANEL_PASSWORD)
bot.polling()