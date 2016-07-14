from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import redis
from config import key

r = redis.StrictRedis(host="localhost", port=6379, charset="utf-8", decode_responses=True)


def init_balance(username):
    r.set(username, "0")


def balance(username):
    balance = r.get(username)
    return float(balance)


def execute_tip(from_, to, amount):
    r.set(from_, balance(from_) - amount)
    r.set(to, balance(to) + amount)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def alias():
    pass


def get_balance(bot, update):
    from_username = update.message.from_user['username']
    balance = r.get(from_username)    
    bot.sendMessage(update.message.chat_id, text="Balance for " + from_username + ": " + str(balance))


def tip(bot, update):
    from_username = update.message.from_user['username']
    query = update.message.text
    try:
        (_, to_username, amount) = query.split(' ')
    except ValueError:
        bot.sendMessage(update.message.chat_id, text="l2tip: wrong number of arguments")
        return

    if to_username[0] == '@':
        to_username = to_username[1:]

    for username in [from_username, to_username]:
        if not r.exists(username):
            init_balance(username)

    try:
        amount = float(amount)
    except ValueError:
        bot.sendMessage(update.message.chat_id, text="l2tip: amount needs to be a float")
        return

    if amount < 0:
        bot.sendMessage(update.message.chat_id, text="l2tip: do you think this is a motherfucking game")
        return

    execute_tip(from_username, to_username, amount)
    bot.sendMessage(update.message.chat_id, text=from_username + " tipped " + to_username + " " + str(amount))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(key)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tip", tip))
    dp.add_handler(CommandHandler("balance", get_balance))
    dp.add_handler(CommandHandler("help", help))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
