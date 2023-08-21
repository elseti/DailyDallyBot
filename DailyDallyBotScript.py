import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, filters
import mysql.connector
import datetime

### creating connection object ###
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "ElSet7501:)"
)

print(mydb)

### creating mySQL cursor ###
cursor = mydb.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


########### Functions #############

# for using @DillyDailyBot /start outside etc.
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

# /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please help yourself.")



# /getAllBdays Retrieves all birthdays
async def fetch_all_bdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = []
    res2 = ""
    cursor.execute("USE dailydally")

    # get name
    cursor.execute("SELECT name FROM bday")
    for name in cursor:
        res.append("".join(name))

    # get birthday date
    cursor.execute("SELECT birth FROM bday")
    x = 0
    for bday in cursor:
        str_date = bday[0].strftime("%d/%m/%Y")
        res2 += "{}'s birthday is on {}.\n".format(res[x], str_date)
        x +=1
    await context.bot.send_message(chat_id=update.effective_chat.id, text="{}".format(res2))


async def add_bday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        input_list = update.message.text.split(" ")
        if len(input_list) != 3:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage of addBday: /addBday [name (one word, no space)] [birthday (YYYY-MM-DD)]")
            return
        
        name = input_list[1]
        date = input_list[2]
        
        date_list = date.split("-")
        # print(date_list)
        # date validation (still prone to errors)
        # if not ((date_list[0]>1000 and date_list[0]<3000) or (date_list[1]>0 and date_list[1]<13) or (date_list[2]>0 and date_list[2]<32)):
        #     await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage of addBday: /addBday [name (one word, no space)] [birthday (YYYY-MM-DD)]")
        #     return

        cursor.execute("USE dailydally")
        cursor.execute("INSERT INTO bday (name, birth) VALUES ('{}', '{}');".format(name, date))
        mydb.commit() #don't forget this!

        cursor.execute("SELECT * FROM bday")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Added {}'s birthday on {}!".format(name, date))
    
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, something went wrong. Check that your usage of the command is correct. Usage of addBday: /addBday [name (one word, no space)] [birthday (YYYY-MM-DD)]")




########### MAIN #############

if __name__ == '__main__':
    application = ApplicationBuilder().token('6581799878:AAGz7cScOn09i74LhM_e5Gw1Bs4mFouRXXM').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler("addBday", add_bday))
    application.add_handler(CommandHandler('getAllBdays', fetch_all_bdays))
    application.add_handler(InlineQueryHandler(inline_caps))


    application.run_polling()