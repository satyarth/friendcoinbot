from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import redis
from math import isnan, isinf
from config import key

r = redis.StrictRedis(host="localhost", port=6379, charset="utf-8", decode_responses=True)

class NotFound(Exception):
    pass

def init_balance(username):
    r.set(username, "0")


def balance(username):
    balance = r.get(username)
    if balance == None:
        raise NotFound
    return float(balance)


def truncate(num):
    return '{0:g}'.format(num) + "💦"


def execute_tip(from_, to, amount):
    r.set(from_, balance(from_) - amount/2)
    r.set(to, balance(to) + amount)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def alias():
    pass


def get_balance(bot, update):
    from_username = update.message.from_user['username']
    query = update.message.text.split(' ')
    print(query)
    if len(query) == 1:
        bot.sendMessage(update.message.chat_id, text="Balance for " + from_username + ": " + truncate(balance(from_username)))
    elif query[1] == '*':
        response = "Balances:\n"
        deets = []
        for username in r.keys('*'):
            print(username)
            deets.append((username, balance(username)))
            print(deets)
        print(deets)
        for deet in sorted(deets, key=lambda -x:x[1]):
            response += deet[0] + ": " + truncate(deet[1]) + "\n"
        bot.sendMessage(update.message.chat_id, text=response)
    else:
        response = "Balances:\n"
        for username in query[1:]:
            try:
                response += username + ": " + truncate(balance(username)) + "\n"
            except NotFound:
                response += "l2tip: " + username + " doesn't exist\n"
        bot.sendMessage(update.message.chat_id, text=response)


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

    if isnan(amount) or isinf(amount):
        bot.sendMessage(update.message.chat_id, text="l2tip: u cheeky scrub")
        return

    if from_username == to_username:
        bot.sendMessage(update.message.chat_id, text="l2tip: ))<>(( back and forth... forever")
        return

    if amount < 0:
        bot.sendMessage(update.message.chat_id, text="l2tip: amount needs to be non-negative. do you think this is a motherfucking game?")
        return

    execute_tip(from_username, to_username, amount)
    bot.sendMessage(update.message.chat_id, parse_mode='Markdown', text="*"+to_username + "* was tipped *" + truncate(amount) + "* by *" + from_username+"*\n" \
                    + to_username +": "+ truncate(balance(to_username))+"\n" \
                    + from_username +": "+ truncate(balance(from_username)))


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
