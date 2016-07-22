from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from math import isnan, isinf
import shelve
from config import key

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
    return '{0:g}'.format(num) + "💦"

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')

def get_balance(bot, update):
    response = "Balances:\n"
    for username in sorted(r.keys(), key=lambda x:-balance(x)):
        response += username + ": " + truncate(balance(username)) + "\n"
    bot.sendMessage(update.message.chat_id, text=response)

def utalk(bot, update):
    talker = update.message.from_user['username']
    makes_bank(talker, 0.1)
    

def main():
    updater = Updater(key)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("balances", get_balance))
    dp.add_handler(MessageHandler([Filters.text], utalk))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    with shelve.open("balances.pickled") as db:
        r = db
        main()
