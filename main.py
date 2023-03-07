import time
import database
from config import bot_token
import telebot
import Functionalities

from telebot.types import ReplyKeyboardMarkup, ForceReply

#  Bot instance
bot = telebot.TeleBot(bot_token)

#  Check if database already exist, and create it if not.
database.check_and_create_tables()

#  Users and daily users global variables.
users = {}
daily_payment_users = {}


#  Reacts to /start command.
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Use /new_user to create a new profile.\n"
                                      "Use /calculate_daily_payment for calculate your daily income.")


#  Reacts to /new_user command.
@bot.message_handler(commands=['new_user'])
def create_user(message):
    markup = ForceReply()
    name = bot.send_message(message.chat.id, "What is your name?", reply_markup=markup)

    bot.register_next_step_handler(name, ask_starting_hour)


#  Reacts to /help command, and send a message with all commands and a link to my github.
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
Hi! My name is Extra Hours bot. I can help you in many ways!

Use /calculate_daily_payment to see how much you would be paid in one day. I will keep your hourly income
in my database, so you don´t have to introduce it again every time you use it.

Use /reset_price_per_hour if you want me to delete that hourly income of my database, and I will 
asks you again your hourly income when you want to calculate another daily payment. I hope you got a rise!

Use /new_user to create a profile in my database. I will ask you your work schedule, and your hourly income.
I will use it to help you calculate your <b>extra hours!</b>

Use /check_valid_hour to check if I can understand a certain format of hour. (I know, I'm a bit special!)

I'm still under construction, so don't be mad with me if I don´t work correctly!

If you have any questions or want to report a bug, contact my creator on github : <a href="https://github.com/FernandooMarinn">FernandooMarinn</a>
    """
    bot.send_message(message.chat.id, help_message, parse_mode="html")


#  Reacts to /check_valid_hour command.
@bot.message_handler(commands=['check_valid_hour'])
def start_check_valid_hour(message):
    markup = ForceReply()
    hour = bot.send_message(message.chat.id, "What hour do you want to check?", reply_markup=markup)
    bot.register_next_step_handler(hour, finish_check_valid_hour)


#  Reacts to /calculate_daily_payment command.
@bot.message_handler(commands=['calculate_daily_payment'])
def ask_arrival_time(message):
    markup = ForceReply()

    arrival = bot.send_message(message.chat.id, "when do the work start?", reply_markup=markup)

    bot.register_next_step_handler(arrival, ask_leaving_time)


def ask_leaving_time(message):
    #  Check if the message body is an hour, and transform it to a valid format if possible.
    o_clock_hour = Functionalities.check_o_clock_hours(message.text)
    if not o_clock_hour:
        hour = message.text
    else:
        hour = o_clock_hour

    #  If the format is not valid, sends a error message to the user.
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")

    else:
        markup = ForceReply()
        #  Try to save the information in a diccionary, with the user id as key. It creates if it doesn't exist.
        try:
            daily_payment_users[message.chat.id]["arrival_time"] = hour
        except KeyError:
            daily_payment_users[message.chat.id] = {}
            daily_payment_users[message.chat.id]["arrival_time"] = hour

        #  Ask another question, and continues in ask_price_per_hour.
        departure = bot.send_message(message.chat.id, "When do the work finish?", reply_markup=markup)

        bot.register_next_step_handler(departure, ask_price_per_hour)


def ask_price_per_hour(message):
    #  Check if the message body is an hour, and transform it to a valid format if possible.
    o_clock_hour = Functionalities.check_o_clock_hours(message.text)
    if not o_clock_hour:
        hour = message.text
    else:
        hour = o_clock_hour

    #  If the format is not valid, sends a error message to the user.
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")

    else:
        daily_payment_users[message.chat.id]["exit_time"] = hour
        #  Here is calling the database, trying to read if there is already an hourly income for this id.
        check_database = database.check_and_return_daily_user(message.chat.id)

        #  If the user doesn't exists in the database, ask for a hourly income, and continues in final_price_per_hour
        if not check_database:
            markup = ForceReply()
            payment_per_hour = bot.send_message(message.chat.id, "What is the payment per hour?", reply_markup=markup)

            bot.register_next_step_handler(payment_per_hour, final_price_per_hour)
        else:
            #  If it does exits, there is no need to ask it again. This send the daily income to the user.
            payment_per_hour = check_database
            daily_payment_users[message.chat.id]["payment_per_hour"] = payment_per_hour
            total_payment = Functionalities.calculate_total_day_payment(daily_payment_users[message.chat.id])

            bot.send_message(message.chat.id, "Total payment would be {}€".format(total_payment))


def final_price_per_hour(message):
    #  If there wasn't a register in the database, this checks if the message is a number.
    check_if_number = Functionalities.check_if_float_number(message.text)
    #  If not, send a message of error and stop.
    if not check_if_number:
        bot.send_message(message.chat.id, "That is not a number! Please try again.")
    else:
        #  Else, it saves the hourly income, and sends it to the user.
        hourly_income = check_if_number
        daily_payment_users[message.chat.id]["payment_per_hour"] = hourly_income

        total_payment = Functionalities.calculate_total_day_payment(daily_payment_users[message.chat.id])

        #  Here it saves the hourly income in the database, so the next time there is no need to ask again.
        database.introduce_daily_user_to_database(message.chat.id, daily_payment_users[message.chat.id])

        bot.send_message(message.chat.id, "Total payment would be {}€".format(total_payment))


#  Reacts to a variety of types of messages.
@bot.message_handler(content_types=['document', 'audio', 'video', 'photo', 'voice'])
def audio_doc_video(message):

    if message.content_type == 'document':
        bot.reply_to(message, "Uuuhhh, a document. I hope you haven't confused me with your local city council.")

    elif message.content_type == 'audio' or message.content_type == 'voice':
        bot.reply_to(message, "I can't hear you! What are you saying?")

    elif message.content_type == 'video':
        bot.reply_to(message, "I'm sure that an awesome video. Unfortunately I can't process it!")

    elif message.content_type == 'photo':
        bot.reply_to(message, "I hope that is a beautiful photo and you enjoy it . BECAUSE I CAN'T SEE IT!",
                     parse_mode="html")
    bot.send_message(message.chat.id, "I'm a bot. You remember?")


#  Reacts to a sticker message.
@bot.message_handler(content_types=['sticker'])
def echo_sticker(message):
    sticker_id = message.sticker.file_id
    bot.reply_to(message, "I'm just supposing this is a cool stiker, and I'm sending it to you twice.")
    bot.send_sticker(message.chat.id, sticker_id)
    bot.send_sticker(message.chat.id, sticker_id)


#  Reacts to /reset_price_per_hour command
@bot.message_handler(commands=['reset_price_per_hour'])
def reset_price_per_hour(message):
    #  Here it tries to delete an user from the database of daily income users.
    deleting_user = database.delete_daily_user(message.chat.id)
    #  It there was anything affected, sends a successfully message.
    if deleting_user == 1:
        bot.reply_to(message, "You have made a reset of your hourly rate!")
    #  It there wasn't anything affected, informs the user that anything changed.
    elif deleting_user == 0:
        bot.reply_to(message, "You don't have an hourly rate! You can't reset it yet!")


#  This reacts to the rest of the messages that are not supported above. Tell the user to use its commands.
@bot.message_handler(func=lambda x: True)
def answer_unknown_texts(message):
    bot.reply_to(message, "I'm sorry! I don't understand you! Please use /help and use my commands.")


def finish_check_valid_hour(message):
    if Functionalities.check_hour(message.text):
        bot.send_message(message.chat.id, "It is a correct format.")

    elif Functionalities.check_o_clock_hours(message.text) != False:
        transformed_hour = Functionalities.check_o_clock_hours(message.text)
        bot.send_message(message.chat.id, "Your hour has been transformed to {}".format(transformed_hour))
    else:
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")


# ----------------------------------------------------------------------


def ask_starting_hour(message):
    name = message.text
    bot.send_message(message.chat.id, "Welcome {}!".format(name))
    bot.send_message(message.chat.id, "Lets continue with a few questions about your job.")

    #  We are creating an user diccionary inside our global users diccionary.
    users[message.chat.id] = {"name": name}

    bot.send_chat_action(message.chat.id, "typing")

    markup = ForceReply()
    starting_hour = bot.send_message(message.chat.id, "What time do you usually start work? (from 00:00 to 23:59)",
                                     reply_markup=markup)

    bot.register_next_step_handler(starting_hour, ask_finishing_hour)


def ask_finishing_hour(message):
    hour = Functionalities.check_o_clock_hours(message.text)
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:
        bot.send_chat_action(message.chat.id, "typing")

        users[message.chat.id]["start_hour"] = hour

        markup = ForceReply()
        finishing_hour = bot.send_message(message.chat.id, "Nice! And when do you finish?", reply_markup=markup)

        bot.register_next_step_handler(finishing_hour, final_time_question)


def final_time_question(message):
    hour = Functionalities.check_o_clock_hours(message.text)
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:

        users[message.chat.id]["finish_hour"] = hour

        bot.send_chat_action(message.chat.id, "typing")

    markup = ForceReply()
    hourly_income = bot.send_message(message.chat.id, "How much are you paid per hour?", reply_markup=markup)

    bot.register_next_step_handler(hourly_income, ask_money_per_hour)


def ask_money_per_hour(message):
    hourly_income = message.text
    if not Functionalities.check_if_float_number(hourly_income):
        bot.send_message(message.chat.id, "You haven't entered a number! Please try again.")
    else:
        users[message.chat.id]["payment_per_hour"] = hourly_income

        bot.send_message(message.chat.id, "Good! Now some questions about your work days.")

        work_days = {"Monday": None, "Tuesday": None, "Wednesday": None, "Thursday": None, "Friday": None,
                     "Saturday": None, "Sunday": None, "number_of_day": 0}
        users[message.chat.id]["work_days"] = work_days

        ask_working_days(message)


def ask_working_days(message):
    current_day = Functionalities.calculate_current_day(users[message.chat.id])
    bot.send_chat_action(message.chat.id, "typing")

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Press a button.")
    markup.add("yes", "no")

    answer = bot.send_message(message.chat.id, "Do you work on {}?".format(current_day), reply_markup=markup)

    bot.register_next_step_handler(answer, write_working_day)


def write_working_day(message):
    current_day = Functionalities.calculate_current_day(users[message.chat.id])
    if message.text.lower() == "yes":
        users[message.chat.id]["work_days"][current_day] = 1
    elif message.text.lower() == "no":
        users[message.chat.id]["work_days"][current_day] = 0
    else:
        bot.send_message(message.chat.id, "You have entered a wrong input! Please try again and use the buttons!")
        del users[message.chat.id]
        return False

    if users[message.chat.id]["work_days"]["number_of_day"] < 6:
        users[message.chat.id]["work_days"]["number_of_day"] += 1
        ask_working_days(message)
    else:
        save(message.chat.id)


def save(telegram_id):
    print(users[telegram_id])
    check_data_saving = database.introduce_new_user_to_database(telegram_id, users[telegram_id])
    print(check_data_saving)
    if check_data_saving == False:
        database.delete_user(telegram_id)
        notify_error_creating_user(telegram_id)
    else:
        bot.send_message(telegram_id, "Nice {}! You have successfully created your user!"
                         .format(users[telegram_id]["name"]))


def notify_error_creating_user(id):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Introduce your preference")
    markup.add("Keep older user", "Create new one")
    check = bot.send_message(id, "Ooops, seems like you are already in my database. Do you want to delete "
                                 "the former user and create a new one?", reply_markup=markup)

    bot.register_next_step_handler(check, delete_or_keep_user)


def delete_or_keep_user(message):
    if message.text.lower() == "keep older user":
        bot.send_message(message.chat.id, "Perfect! You will keep your current profile.")
    elif message.text.lower() == "create new one":
        database.delete_user(message.chat.id)
        database.introduce_new_user_to_database(message.chat.id, users[message.chat.id])
        bot.send_message(message.chat.id, "Nice! I just deleted the old user, and introduced the new one.")
    else:
        bot.send_message(message.chat.id, "It seems like you introduced a wrong value. I'm sorry, but you have to "
                                          "start again!")


""" to do:
       
        OJO! Que luego puede ser que lo quieras modificar. No escribas dos veces el mismo codigo.
        
        Una vez terminado, eliminar NO EL DICCIONARIO, si no la clave correspondiente
        
        ask every user it's weekly days of work. Se puede utilizar un botón para ver si es siempre igual o no.
        Introduce every day in the data base, related with the working hours
        Añadir la biblioteca time o datatime para que sea facil para un usuario empezar y acabar un turno.
        Conectar con algun tipo de biblioteca que automatice los días de la semana(NO EN DB). (Imprimir a final de mes)
        
        La conexion a la base de datos tiene que ser lo más rapida posible, para evitar errores (abrir y cerrar)
        
        AÑADIR HOURLY_INCOME A USERS
        
        
        
"""

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/help", "Show functions to use with the bot."),
        telebot.types.BotCommand("/new_user", "Create a new profile."),
        telebot.types.BotCommand("/check_valid_hour", "Check if an hour format is correct to use it with the bot."),
        telebot.types.BotCommand("/calculate_daily_payment", "For cheking your daily income, depending on hours."),
        telebot.types.BotCommand("/reset_price_per_hour", "Ask you again your hourly rate when"
                                                          " using /calculate_daily_payment")
    ])

    print("\n Working...\n")
    bot.infinity_polling()
