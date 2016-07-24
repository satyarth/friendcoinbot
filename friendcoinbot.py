from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from math import isnan, isinf
import shelve
from config import key
import re

r = None

class NotFound(Exception):
    pass

def balance(username):
    return r[username]
    
def makes_bank(username, dolla):
    if username not in r:
        r[username] = 0
    
    r[username] += dolla

def truncate(num):
    return '{0:g}'.format(num) + "🔥"

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')

def get_balance(bot, update):
    response = "Balances:\n"
    for username in sorted(r.keys(), key=lambda x:-balance(x)):
        response += username + ": " + truncate(balance(username)) + "\n"
    bot.sendMessage(update.message.chat_id, text=response)

def is_lol(str):
    str = str.lower()
    lols = [
        "l[aeiou][aeiou]*l[sz]?",
        "[hae][hae]*",
        "kek",
        "rofl",
        "lmao",
        "stf",
        "[waough][waough]*",
        "wow[sz]er[sz]",
    ]
    exclusions = ["ee*hh*", "aa*hh*"]
    
    any_matches = lambda patterns: any(re.fullmatch(pattern, str) for pattern in patterns)
    
    print(str, any_matches(lols), any_matches(exclusions))
    return any_matches(lols) and not any_matches(exclusions)
    
previous_messages = {}

def previous_message(update):
    return previous_messages[update.message.chat_id]
    
def utalk(bot, update):
    if update.message.chat.type == "private":
        return
    
    talker = update.message.from_user['username']
    makes_bank(talker, 0.1)
    
    first_word = update.message.text.split()[0]
    
    if is_lol(first_word):
        previous_talker = previous_message(update).from_user['username']
        print("lol from " + talker + " to " + previous_talker)
        makes_bank(previous_talker, 1)
        makes_bank(talker, 0.2)
        
    previous_messages[update.message.chat_id] = update.message
    
def appeal(bot, update):
    bot.sendMessage(update.message.chat_id, text="Appeal denied, bitch")
    
def main():
    updater = Updater(key)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("appeal", appeal))
    dp.add_handler(CommandHandler("balances", get_balance))
    dp.add_handler(MessageHandler([Filters.text], utalk))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    with shelve.open("balances.pickled") as db:
        r = db
        main()
