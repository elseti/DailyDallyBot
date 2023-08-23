import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, filters
import mysql.connector

### creating connection object ###
mydb = mysql.connector.connect(
    host = "sql6.freemysqlhosting.net",
    user = "sql6641882",
    password = "7WcdwzAA5f",
    port = "3306"
)

db_name = "sql6641882"
### creating mySQL cursor ###
cursor = mydb.cursor()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""
    Welcome to DailyDally Bot! List of commands:
                                
    /addBday [name] [YYYY-MM-DD]: Add a name and birthday.
    /getBday [name] Gets someone's birthday.
    /getAllBdays: Fetches all birthdays stored.
    /deleteAllBdays: Deletes all birthdays.
    /deleteBday [name]: Delete someone's birthday.

    """)

# /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= """
    List of commands:
                                
    /addBday [name] [YYYY-MM-DD]: Add a name and birthday.
    /getBday [name] Gets someone's birthday.
    /getAllBdays: Fetches all birthdays stored.
    /deleteAllBdays: Deletes all birthdays.
    /deleteBday [name]: Delete someone's birthday.

    """)

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text= "Doing setup")
    cursor.execute("USE {};".format(db_name))
    cursor.execute("""CREATE TABLE bday(id INT unsigned NOT NULL AUTO_INCREMENT,
                   name VARCHAR(150) NOT NULL,
                   birth DATE NOT NULL,
                   uid INT NOT NULL,
                   PRIMARY KEY (id)
                );""")
# (
#   id              INT unsigned NOT NULL AUTO_INCREMENT, # Unique ID for the record
#   name            VARCHAR(150) NOT NULL,                # Name of the cat
#   owner           VARCHAR(150) NOT NULL,                # Owner of the cat
#   birth           DATE NOT NULL,                        # Birthday of the cat
#   PRIMARY KEY     (id)                                  # Make the id the primary key
# );





########### MAIN #############

if __name__ == '__main__':
    application = ApplicationBuilder().token('6581799878:AAGz7cScOn09i74LhM_e5Gw1Bs4mFouRXXM').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('setup', setup))

    application.run_polling()

