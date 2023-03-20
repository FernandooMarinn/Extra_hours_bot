from database_package import database
from config.config import bot_token
import telebot
from Functionalities import Functionalities

from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove

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
I will use it to help you calculate your <b>extra hours!</b> Check /help_extra_hours for more info.

Use /check_valid_hour to check if I can understand a certain format of hour. (I know, I'm a bit special!)

I'm still under construction, so don't be mad with me if I don´t work correctly!

If you have any questions or want to report a bug, contact my creator on github :
<a href="https://github.com/FernandooMarinn">FernandooMarinn</a>
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
        #  Try to save the information in a dictionary, with the user id as key. It creates if it doesn't exist.
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
    bot.reply_to(message, "I'm just supposing this is a cool sticker, and I'm sending it to you twice.")
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


@bot.message_handler(commands=['edit'])
def edit(message):
    bot.send_message(message.chat.id, "This is still under construction, but it will let you edit your work "
                                      "schedule and extra hours.")


@bot.message_handler(commands=['start_work'])
def starting_work(message):
    current_day = Functionalities.receive_current_day()
    current_hour = Functionalities.receive_current_hour()

    check_day = database.check_if_already_exist_in_days("*", "day", current_day, message.chat.id)
    if check_if_user_exist(message.chat.id):

        if check_day is None:
            database.introduce_many_to_days(["day", "start_hour", "telegram_id"],
                                            [current_day, current_hour, message.chat.id])
            bot.send_message(message.chat.id, "Your start hour has been registered!")

        else:
            check_start_hour = database.check_if_already_exist_in_days("start_hour", "day", current_day, message.chat.id)

            if check_start_hour is None:
                database.update_one_to_days("start_hour", current_hour, "day", current_day, message.chat.id)
                bot.send_message(message.chat.id, "Your start hour has been registered!")

            else:
                bot.send_message(message.chat.id, "It seems that there is already a starting hour for today.\n"
                                                  "If you want to change it, please use /edit")


@bot.message_handler(commands=['end_work'])
def end_work(message):
    #  Get current day and current hour using datetime library
    current_day = Functionalities.receive_current_day()
    current_hour = Functionalities.receive_current_hour()

    #  Checks if user already exist, and continues only if so.
    if check_if_user_exist(message.chat.id):
        #  Check if current day already exist in database.
        check_day = database.check_if_already_exist_in_days("*", "day", current_day, message.chat.id)

        if check_day is None:
            #  If does not exist yet there isn't a start hour, so it gets the usual start hour from the user database.

            user_start_hour = database.get_usual_hour(message.chat.id, "start_hour")[0]
            #  It checks if the close hour is bigger than the start hour (same day) or is lower (next day)

            if Functionalities.check_if_lower_hour(current_hour, user_start_hour) == user_start_hour:
                #  If the lower hour is the start, it introduce it to the database with the finish hour.
                database.introduce_many_to_days(["day", "start_hour", "finish_hour", "telegram_id"],
                                                [current_day, user_start_hour, current_hour, message.chat.id])

                bot.send_message(message.chat.id, "Your finish hour has been registered!")

            else:
                #  If the lower hour is the finish one, it means that it happened in another day.
                end_after_midnight(current_hour, message.chat.id, user_start_hour)

        else:
            #  If the day already exist, it only updates finish hour in the database.
            check_finish_hour = database.check_if_already_exist_in_days("finish_hour", "day",
                                                                        current_day, message.chat.id)
            if check_finish_hour[0] is None:
                database.update_one_to_days("finish_hour", current_hour, "day", current_day, message.chat.id)
                bot.send_message(message.chat.id, "Your finish hour has been registered!")
            else:
                bot.send_message(message.chat.id, "It seems that there is already a finish hour."
                                                  " Please use /edit to change it.")


def end_after_midnight(current_hour, telegram_id, user_start_hour):
    #  Uses the current day information to calculate the previous day.
    previous_day = Functionalities.get_previous_day()
    #  Checks if the previous day exist in the database.
    check_day = database.check_if_already_exist_in_days("*", "day", previous_day, telegram_id)

    if check_day is None:
        #  If doesn't exist, it introduces the values to the previous day.
        database.introduce_many_to_days(["day", "start_hour", "finish_hour", "telegram_id"],
                                        [previous_day, user_start_hour, current_hour, telegram_id])

    else:
        check_finish_hour = database.check_if_already_exist_in_days("finish_hour", "day", previous_day, telegram_id)
        #  If it does exist, checks if there is already a finish hour.
        if check_finish_hour is None:
            #  If there is no finish hour, updates it with the current hour.
            database.update_one_to_days("finish_hour", current_hour, "day", previous_day, telegram_id)
            bot.send_message(telegram_id, "Your start hour has been registered!")

        else:
            #  If there is a register, sends a message of error.
            bot.send_message(telegram_id, "It seems that there is already a finish hour."
                                          " Please use /edit to change it.")


def check_if_user_exist(id):
    #  Check if an user exist in the database, and return True if so, and False if not.
    if database.check_if_user_exits(id) is None:
        bot.send_message(id, "You haven't created an user yet! Please use /new_user first.")
        return False
    else:
        return True


@bot.message_handler(commands=['finish_month'])
#  Reacts to the command /end_month, and calculate total extra hours, and send two messages with all the information.
def calculate_end_of_the_month(message):
    #  If the user exist
    if check_if_user_exist(message.chat.id):
        #  It saves the telegram id and the total days registries of the month.
        telegram_id = message.chat.id
        days = database.end_month_get_hours(telegram_id)
        #  If there are no registries, send an error message.
        if days == []:
            bot.send_message(message.chat.id, "There are not hours! Use /help_extra_hours to know how I work!")
        else:
            #  It gets start and end hours from the database.
            usual_start_hour = database.get_usual_hour(telegram_id, "start_hour")
            usual_end_hour = database.get_usual_hour(telegram_id, "finish_hour")
            #  Gets also the free days from database.
            free_days = database.get_work_days(telegram_id)
            #  Calculates free days pattern, with True when the user works, and False when not.
            day_pattern = Functionalities.free_days_pattern(free_days)
            #  Calculates the days that have no registry, and adds them to the others that have it.
            whole_month_days = Functionalities.add_all_days(days, day_pattern, usual_start_hour, usual_end_hour)
            #  Calculates total extra hours.
            total_days = Functionalities.end_month_add_extra_hours_to_days(whole_month_days,
                                                                           [usual_start_hour, usual_end_hour],
                                                                           day_pattern)

            #  Gets the total hourly payment from the database.
            money_per_hour = database.get_money_per_hour(telegram_id)
            #  Creates a long message, with html format.
            complete_message = Functionalities.create_message_end_of_the_month(total_days, money_per_hour)
            #  Sends it.
            bot.send_message(telegram_id, complete_message, parse_mode='html')
            #  Creates a simplified message, with the same information, and rounded hours.
            simplified_message = Functionalities.create_simplified_message(total_days, money_per_hour)
            #  Sends it.
            bot.send_message(telegram_id, simplified_message, parse_mode='html')
            #  Continues in finish_month.
            finish_month(telegram_id)


#  This reacts to the command /help_extra_hours and send a little explanation about it's functionalities.
@bot.message_handler(commands=['help_extra_hours'])
def help_extra_hours(message):
    message_to_send = """
-First, you have to create a new user (If you don't have it!). I will ask you some questions about your job.

-After that, you can use my commands /start_work and /end_work one you enter or exit your job. The hour 
when I receive your message will be saved in your database. I you don't send me any message, I will suppose
that you are entering/leaving in time.

-When you want to calculate your current hours, or the month is finishing, use /end_month command and I will send
you all the info in my database, in two ordered messages. One of them with all the information, and another one 
simplified, so it is easier to understand.
    """

    bot.send_message(message.chat.id, message_to_send)


#  This reacts to the rest of the messages that are not supported above. Tell the user to use its commands.
@bot.message_handler(func=lambda x: True)
def answer_unknown_texts(message):
    bot.reply_to(message, "I'm sorry! I don't understand you! Please use /help and use my commands.")


def finish_check_valid_hour(message):
    #  Takes a message and check if there is an hour in the inside, and corrects it.
    if Functionalities.check_hour(message.text):
        #  If it is exactly the format the bot uses (hh:mm)
        bot.send_message(message.chat.id, "It is a correct format.")

    elif Functionalities.check_o_clock_hours(message.text) != False:
        #  If it is an o'clock hour (h) or an hour with minutes of 3 digits (h:mm)
        transformed_hour = Functionalities.check_o_clock_hours(message.text)
        bot.send_message(message.chat.id, "Your hour has been transformed to {}".format(transformed_hour))

    else:
        #  If it is not correct, or is not an hour.
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")


# ----------------------------------------------------------------------


def ask_starting_hour(message):
    #  Get user name from message text, and gives a welcome.
    name = message.text
    bot.send_message(message.chat.id, "Welcome {}!".format(name))
    bot.send_message(message.chat.id, "Lets continue with a few questions about your job.")

    #  It creates an user dictionary inside our global users dictionary.
    users[message.chat.id] = {"name": name}

    #  Sends typing action, and ask start work hour.
    bot.send_chat_action(message.chat.id, "typing")
    markup = ForceReply()
    starting_hour = bot.send_message(message.chat.id, "What time do you usually start work? (from 00:00 to 23:59)",
                                     reply_markup=markup)

    #  Continues in ask_finish_hour.
    bot.register_next_step_handler(starting_hour, ask_finishing_hour)


def ask_finishing_hour(message):
    #  Checks if is a known format, and tries to convert it.
    hour = Functionalities.check_o_clock_hours(message.text)
    if not Functionalities.check_hour(hour):
        #  If it is not a valid hour, send a error message.
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:
        bot.send_chat_action(message.chat.id, "typing")
        #  Saves the hour as start_hour in users variable.
        users[message.chat.id]["start_hour"] = hour

        markup = ForceReply()
        #  Ask at what hour the work finishes.
        finishing_hour = bot.send_message(message.chat.id, "Nice! And when do you finish?", reply_markup=markup)
        #  Continues in final_time_question.
        bot.register_next_step_handler(finishing_hour, final_time_question)


def final_time_question(message):
    hour = Functionalities.check_o_clock_hours(message.text)
    #  If the message does not contain a valid hour format, it sends an error message.
    if not Functionalities.check_hour(hour):
        error_text = Functionalities.wrong_hour_format_text()
        bot.reply_to(message, error_text, parse_mode="html")
    else:
        #  Otherwise, it stored it in the global variable.
        users[message.chat.id]["finish_hour"] = hour

        bot.send_chat_action(message.chat.id, "typing")

    markup = ForceReply()
    #  Ask how much are the user paid by hour.
    hourly_income = bot.send_message(message.chat.id, "How much are you paid per hour?", reply_markup=markup)
    #  Continues in ask_money_per_hour
    bot.register_next_step_handler(hourly_income, ask_money_per_hour)


def ask_money_per_hour(message):
    hourly_income = message.text
    if not Functionalities.check_if_float_number(hourly_income):
        #  If the message is not a number (integer or float) sends an error message and deletes the variable.
        bot.send_message(message.chat.id, "You haven't entered a number! Please try again.")
        del users[message.chat.id]
    else:
        #  Store the value in the global variable.
        users[message.chat.id]["payment_per_hour"] = hourly_income
        #  Ask about work days.
        bot.send_message(message.chat.id, "Good! Now some questions about your work days.")
        #  Creates a dictionary with every day of the week, and a counter (0 = Monday, 6 = Sunday)
        work_days = {"Monday": None, "Tuesday": None, "Wednesday": None, "Thursday": None, "Friday": None,
                     "Saturday": None, "Sunday": None, "number_of_day": 0}
        #  Store the dictionary in the user variable.
        users[message.chat.id]["work_days"] = work_days
        #  Continues in ask_working_days
        ask_working_days(message)


def ask_working_days(message):
    #  Get the string of the day that is currently asking
    current_day = Functionalities.calculate_current_day(users[message.chat.id])
    bot.send_chat_action(message.chat.id, "typing")

    #  Show two buttons, yes or no, and let the user choose.
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Press a button.")
    markup.add("yes", "no")

    #  Ask if the user works on the currently asking day.
    answer = bot.send_message(message.chat.id, "Do you work on {}?".format(current_day), reply_markup=markup)

    #  Continues in write_working_day.
    bot.register_next_step_handler(answer, write_working_day)


def write_working_day(message):
    current_day = Functionalities.calculate_current_day(users[message.chat.id])
    if message.text.lower() == "yes":
        #  If user answer is yes, store a 1 in that day in the dictionary (True)
        users[message.chat.id]["work_days"][current_day] = 1

    elif message.text.lower() == "no":
        #  If user answer is yes, store a 0 in that day in the dictionary (False)
        users[message.chat.id]["work_days"][current_day] = 0

    else:
        #  If the input is not correct, sends error message, deletes user variable and returns False.
        bot.send_message(message.chat.id, "You have entered a wrong input! Please try again and use the buttons!")
        del users[message.chat.id]
        return False

    #  While the counter is less than 6, adds 1 and goes again to ask_working_days.
    if users[message.chat.id]["work_days"]["number_of_day"] < 6:
        users[message.chat.id]["work_days"]["number_of_day"] += 1
        ask_working_days(message)

    else:
        #  When days are finished, continues in save.
        save(message.chat.id)


def save(telegram_id):
    #  It checks if the user already exist and saves it if possible.
    check_data_saving = database.introduce_new_user_to_database(telegram_id, users[telegram_id])

    if check_data_saving == False:
        #  If it already exist, continues in notify_error_creating_user
        notify_error_creating_user(telegram_id)
    else:
        #  Sends a success message and deletes the variable.
        bot.send_message(telegram_id, "Nice {}! You have successfully created your user!"
                         .format(users[telegram_id]["name"]))
        del users[telegram_id]


def notify_error_creating_user(id):
    #  Ask if the user want to delete the former user and create a new one.
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="Introduce your preference")
    markup.add("Keep older user", "Create new one")

    check = bot.send_message(id, "Ooops, seems like you are already in my database. Do you want to delete "
                                 "the former user and create a new one?", reply_markup=markup)

    #  Continues in delete_or_keep_user
    bot.register_next_step_handler(check, delete_or_keep_user)


def delete_or_keep_user(message):
    if message.text.lower() == "keep older user":
        #  If user wants to keep the older user, sends a message and deletes its variable.
        bot.send_message(message.chat.id, "Perfect! You will keep your current profile.")
        del users[message.chat.id]

    elif message.text.lower() == "create new one":
        #  Deletes older user from the database, insert the new one, sends a message and deletes variable.
        database.delete_user(message.chat.id)
        database.delete_work_days(message.chat.id)
        database.delete_days(message.chat.id)

        database.introduce_working_days_to_database(message.chat.id, users[message.chat.id])
        database.introduce_new_user_to_database(message.chat.id, users[message.chat.id])

        bot.send_message(message.chat.id, "Nice! I just deleted the old user, and introduced the new one.")
        del users[message.chat.id]

    else:
        #  If the answer is different, ask to start again and deletes the variable.
        bot.send_message(message.chat.id, "It seems like you introduced a wrong value. I'm sorry, but you have to "
                                          "start again!")
        del users[message.chat.id]


def finish_month(telegram_id):
    #  Ask if user wants to delete all days registries, and start a new month.
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="This can't be undone!!")
    markup.add("yes", "no")
    confirm = bot.send_message(telegram_id, "Do you want to start a new month and delete all the days"
                                            " from the database?", reply_markup=markup)
    #  Makes a double confirmation in delete_days_confirm.
    bot.register_next_step_handler(confirm, delete_days_confirm)


def delete_days_confirm(message):
    markup = ReplyKeyboardRemove()
    #  If answer is no, sends a message.
    if message.text.lower() == "no":
        bot.send_message(message.chat.id, "Ok! Remember to delete the days at the end of the month!",
                         reply_markup=markup)

    #  If is yes, makes a double confirm.
    elif message.text.lower() == "yes":
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder="This can't be undone!")
        markup.add("yes", "no")
        second_confirm = bot.send_message(message.chat.id, "Are you completely sure? This action can not be undone,"
                                                           " and will delete every day register in the database.",
                                          reply_markup=markup)
        #  Continues in final_delete_days.
        bot.register_next_step_handler(second_confirm, final_delete_days)
    else:
        #  If the answer isn't correct, sends an error message.
        bot.send_message(message.chat.id, "It seems that you introduced a wrong value! Please try again.",
                         reply_markup=markup)


def final_delete_days(message):
    markup = ReplyKeyboardRemove()
    #  If the answer is yes, delete every register in days, and sends a message.
    if message.text.lower() == "yes":
        database.delete_days(message.chat.id)
        bot.send_message(message.chat.id, "Days successfully deleted!", reply_markup=markup)
    #  If is no, remember the user to do it at the end of the month.
    elif message.text.lower() == "no":
        bot.send_message(message.chat.id, "OK! Remember to delete them a the end or start of the month!",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "It seems that you introduced a wrong value! Please try again.",
                         reply_markup=markup)


#  Register the commands to show to the user, and start bot infinity polling.
if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/help", "Show functions to use with the bot."),
        telebot.types.BotCommand("/start_work", "For start your day of work"),
        telebot.types.BotCommand("/end_work", "For finish your day of work"),
        telebot.types.BotCommand("/finish_month", "End month and print out the hours."),
        telebot.types.BotCommand("/new_user", "Create a new profile."),
        telebot.types.BotCommand("/check_valid_hour", "Check if an hour format is correct to use it with the bot."),
        telebot.types.BotCommand("/calculate_daily_payment", "For checking your daily income, depending on hours."),
        telebot.types.BotCommand("/reset_price_per_hour", "Ask you again your hourly rate when"
                                                          " using /calculate_daily_payment")
    ])

    print("\n Working...\n")
    bot.infinity_polling()
