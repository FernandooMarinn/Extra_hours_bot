import time

import database
from config import bot_token
import telebot
import Functionalities

from telebot.types import ReplyKeyboardMarkup, ForceReply

bot = telebot.TeleBot(bot_token)


users = {}
daily_payment_users = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Use /new_user to create a new profile.\n"
                                      "Use /calculate_daily_payment for calculate your daily income.")


@bot.message_handler(commands=['new_user'])
def create_user(message):
    markup = ForceReply()
    name = bot.send_message(message.chat.id, "What is your name?", reply_markup=markup)

    bot.register_next_step_handler(name, ask_starting_hour)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "This will be the help answer.")


@bot.message_handler(commands=['check_valid_hour'])
def start_check_valid_hour(message):
    markup = ForceReply()
    hour = bot.send_message(message.chat.id, "What hour do you want to check?", reply_markup=markup)
    bot.register_next_step_handler(hour, finish_check_valid_hour)


@bot.message_handler(commands=['calculate_daily_payment'])
def ask_arrival_time(message):
    markup = ForceReply()

    arrival = bot.send_message(message.chat.id, "when do the work start?", reply_markup=markup)

    bot.register_next_step_handler(arrival, ask_leaving_time)


@bot.message_handler(content_types=['document', 'audio', 'video', 'photo', 'voice'])
def audio_doc_video(message):
    print("Esto esta funcionando")
    print(message)
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


@bot.message_handler(content_types=['sticker'])
def echo_sticker(message):
    sticker_id = message.sticker.file_id
    bot.reply_to(message, "I'm just supposing this is a cool stiker, and I'm sending it to you twice.")
    bot.send_sticker(message.chat.id, sticker_id)
    bot.send_sticker(message.chat.id, sticker_id)


@bot.message_handler(commands=['reset_price_per_hour'])
def reset_price_per_hour(message):
    #  We are checking if we have deleted anything.
    deleting_user = database.delete_daily_user(message.chat.id)
    if deleting_user == 1:
        bot.reply_to(message, "You have made a reset of your hourly rate!")
    elif deleting_user == 0:
        bot.reply_to(message, "You don't have an hourly rate! You can't reset it yet!")


@bot.message_handler(func= lambda x: True)
def answer_unknown_texts(message):
    bot.reply_to(message, "I'm sorry! I don't understand you! Please use /help and use my commands.")


def ask_leaving_time(message):
    o_clock_hour = Functionalities.check_o_clock_hours(message.text)
    if o_clock_hour != False:
        hour = o_clock_hour
    else:
        hour = message.text

    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")

    else:
        markup = ForceReply()

        try:
            daily_payment_users[message.chat.id]["arrival_time"] = hour
        except KeyError:
            daily_payment_users[message.chat.id] = {}
            daily_payment_users[message.chat.id]["arrival_time"] = hour

        departure = bot.send_message(message.chat.id, "When do the work finish?", reply_markup=markup)

        bot.register_next_step_handler(departure, ask_price_per_hour)



def ask_price_per_hour(message):
    o_clock_hour = Functionalities.check_o_clock_hours(message.text)
    if o_clock_hour != False:
        hour = o_clock_hour
    else:
        hour = message.text
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:
        daily_payment_users[message.chat.id]["exit_time"] = hour
        print(message.chat.id)
        check_database = database.check_and_return_daily_user(message.chat.id)

        if check_database != False:
            payment_per_hour = check_database
            daily_payment_users[message.chat.id]["payment_per_hour"] = payment_per_hour
            total_payment = Functionalities.calculate_total_day_payment(daily_payment_users[message.chat.id])

            bot.send_message(message.chat.id, "Total payment would be {}€".format(total_payment))
        else:
            markup = ForceReply()
            payment_per_hour = bot.send_message(message.chat.id, "What is the payment per hour?", reply_markup=markup)

            bot.register_next_step_handler(payment_per_hour, final_price_per_hour)


def final_price_per_hour(message):

    daily_payment_users[message.chat.id]["payment_per_hour"] = message.text

    total_payment = Functionalities.calculate_total_day_payment(daily_payment_users[message.chat.id])

    database.introduce_daily_user_to_database(message.chat.id, daily_payment_users[message.chat.id])

    bot.send_message(message.chat.id, "Total payment would be {}€".format(total_payment))

    print(daily_payment_users)
    print(daily_payment_users[message.chat.id])



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
    time.sleep(2)

    markup = ForceReply()
    starting_hour = bot.send_message(message.chat.id, "What time do you usually start work? (from 00:00 to 23:59)",
                                     reply_markup=markup)

    bot.register_next_step_handler(starting_hour, ask_finishing_hour)


def ask_finishing_hour(message):
    if not Functionalities.check_hour(message.text):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:
        bot.send_chat_action(message.chat.id, "typing")
        time.sleep(2)

        users[message.chat.id]["start_hour"] = message.text

        markup = ForceReply()
        finishing_hour = bot.send_message(message.chat.id, "Nice! And when do you finish?", reply_markup=markup)

        bot.register_next_step_handler(finishing_hour, final_time_question)


def final_time_question(message):
    if not Functionalities.check_hour(message.text):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:

        users[message.chat.id]["finish_hour"] = message.text

        time.sleep(2)
        bot.send_chat_action(message.chat.id, "typing")

        bot.send_message(message.chat.id, "Nice! Now some questions about your working hours.")

        print(users[message.chat.id])
        print(users)

    bot.register_next_step_handler(message, ask_working_days)


def ask_working_days(message):
    work_days = {"Monday": None, "Tuesday": None, "Wednesday": None, "Thursday": None, "Friday": None,
                 "Saturday": None, "Sunday": None}



def ask_individual_day(chat_id, key):
    markup = ForceReply()
    # ADD BUTTONS!!
    bot.send_message(chat_id, "Do you work on {}?")

""" to do:
       
        OJO! Que luego puede ser que lo quieras modificar. No escribas dos veces el mismo codigo.
        
        Una vez terminado, eliminar NO EL DICCIONARIO, si no la clave correspondiente
        
        ask every user it's weekly days of work. Se puede utilizar un botón para ver si es siempre igual o no.
        Introduce every day in the data base, related with the working hours
        Añadir la biblioteca time o datatime para que sea facil para un usuario empezar y acabar un turno.
        Conectar con algun tipo de biblioteca que automatice los días de la semana(NO EN DB). (Imprimir a final de mes)
        
        La conexion a la base de datos tiene que ser lo más rapida posible, para evitar errores (abrir y cerrar)
        
        
        
"""


if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Give you instructions."),
        telebot.types.BotCommand("/new_user", "Create a new profile."),
        telebot.types.BotCommand("/check_valid_hour", "Check if an hour format is correct to use it with the bot."),
        telebot.types.BotCommand("/calculate_daily_payment", "For cheking your daily income, depending on hours."),
        telebot.types.BotCommand("/reset_price_per_hour", "Ask you again your hourly rate when"
                                                          " using /calculate_daily_payment")
    ])

    print("\n Working...\n")
    bot.infinity_polling()
