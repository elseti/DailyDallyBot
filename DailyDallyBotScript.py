import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, filters
import mysql.connector

### creating connection object ###
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "ElSet7501:)"
)

### creating mySQL cursor ###
cursor = mydb.cursor()

reply = ""

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



# /getAllBdays Retrieves all birthdays
async def fetch_all_bdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = []
    res2 = ""
    cursor.execute("USE dailydally")
    user_id = update.message.chat_id

    # get name
    cursor.execute("SELECT name FROM bday WHERE uid='{}'".format(user_id))        

    for name in cursor:
        res.append("".join(name))
    
    if len(res)==0:
        cursor.reset()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No records found.")
        return

    # get birthday date
    cursor.execute("SELECT birth FROM bday WHERE uid='{}'".format(user_id))
    x = 0
    for bday in cursor:
        str_date = bday[0].strftime("%d/%m/%Y")
        res2 += "{}'s birthday is on {}.\n".format(res[x], str_date)
        x +=1

    cursor.reset()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="{}".format(res2))


async def add_bday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        input_list = update.message.text.split(" ")
        if len(input_list) != 3:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage of addBday: /addBday [name (one word, no space)] [birthday (YYYY-MM-DD)]")
            return
        
        name = input_list[1]
        date = input_list[2]
        user_id = update.message.chat_id

        cursor.execute("USE dailydally")
        cursor.execute("INSERT INTO bday (name, birth, uid) VALUES ('{}', '{}', {});".format(name, date, user_id))
        mydb.commit() # don't forget this!
        cursor.reset() # reset cursor
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Added {}'s birthday on {}!".format(name, date))
    
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, something went wrong. Check that your usage of the command is correct. \nUsage of addBday: /addBday [name (one word, no space)] [birthday (YYYY-MM-DD)]")


async def get_bday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_list = update.message.text.split(" ")
    if len(input_list) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage of addBday: /getBday [name (one word, no space)]")
        return
    
    res = ""
    name = input_list[1]
    user_id = update.message.chat_id

    cursor.execute("USE dailydally")
    cursor.execute("SELECT birth FROM bday WHERE uid='{}' AND name='{}';".format(user_id, name))
    
    res = cursor.fetchone()
    
    if res == None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No record found for {}".format(name))
        return
    
    res = res[0].strftime("%d/%m/%Y")
   
    cursor.reset()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="{}'s birthday is on {}.".format(name, res))


# delete bday
async def delete_bday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_list = update.message.text.split(" ")
    if len(input_list) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage of addBday: /deleteBday [name (one word, no space)]")
        return
    
    name = input_list[1]

    cursor.execute("USE dailydally")
    cursor.execute("DELETE FROM bday WHERE name='{}';".format(name))
    mydb.commit()
    cursor.reset()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Deleted successfully.")



# confirmation for deleting all bdays
async def delete_all_bdays_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    reply_keyboard = [["Delete", "Cancel"]]
    await update.message.reply_text(
        text= "Are you sure you want to delete all records?",
        reply_markup = ReplyKeyboardMarkup(
            keyboard=reply_keyboard, one_time_keyboard=True, input_field_placeholder="Confirm deletion?"
        ),
    )

    return 1

    
async def delete_all_bdays_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Okay.")
    input = update.message.text
    print(input)

    if input == "Delete":
        print("in delete all bdays")
        cursor.execute("USE dailydally")
        cursor.execute("DELETE FROM bday")
        mydb.commit()
        cursor.reset()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Deleted all records successfully.")
    
    elif input == "Cancel":
        print("cancelled")
        cursor.reset()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Operation cancelled.")
    
    return ConversationHandler.END # don't forget to put this to end it


#### conversation handler for deleteAllBDays ####
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('deleteAllBdays', delete_all_bdays_confirmation)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_all_bdays_response)],
    },
    fallbacks=[CommandHandler("start", start)]
)

########### MAIN #############

if __name__ == '__main__':
    application = ApplicationBuilder().token('6581799878:AAGz7cScOn09i74LhM_e5Gw1Bs4mFouRXXM').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('addBday', add_bday))
    application.add_handler(CommandHandler('getAllBdays', fetch_all_bdays))
    application.add_handler(CommandHandler('deleteBday', delete_bday))
    application.add_handler(CommandHandler('getBday', get_bday))
    application.add_handler(InlineQueryHandler(inline_caps))

    application.add_handler(conv_handler)


    application.run_polling()