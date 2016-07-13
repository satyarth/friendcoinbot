#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import redis

r = redis.StrictRedis(host="localhost", port=6379, charset="utf-8", decode_responses=True)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def init_balance(username):
    r.set(username, "0")

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')

def alias():
    pass

def execute_tip(from_, to, amount):
    balance_from = float(r.get(from_))
    r.set(from_, str(balance_from - amount))
    balance_to = float(r.get(to))
    r.set(to, str(balance_to + amount))

def balance(bot, update):
    from_username = update.message.from_user['username']
    balance = r.get(from_username)    
    bot.sendMessage(update.message.chat_id, text="Balance for " + from_username + ": " + str(balance))

def tip(bot, update):
    from_username = update.message.from_user['username']
    query = update.message.text
    try:
        (_, to_username, amount) = query.split(' ')
    except ValueError:
        bot.sendMessage(update.message.chat_id, text="l2tip: too many arguments")

    for username in [from_username, to_username]:
        if not r.exists(username):
            init_balance(username)

    try:
        amount = float(amount)
    except ValueError:
        bot.sendMessage(update.message.chat_id, text="l2tip: amount need to be a float")

    execute_tip(from_username, to_username, amount)
    bot.sendMessage(update.message.chat_id, text=from_username + " tipped " + to_username + " " + str(amount))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("241733792:AAE9DVwsTmad5husDV84-7SSjnAIzJxlv-o")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tip", tip))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("help", help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
