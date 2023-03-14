import datetime


def check_hour(hour):
    """
    Check if an hour format is valid for the bot.
    :param hour:
    :return:
    """
    if not hour:
        return False
    #  If there are not ":" in the hour, is invalid.
    if ":" not in hour:
        return False
    #  Here it divides the hour in hours and minutes.
    divided_hour = hour.split(":")

    hours = divided_hour[0]
    minutes = divided_hour[1]
    #  If there aren't numbers, is invalid.
    if not hours.isdigit() or not minutes.isdigit():
        return False
    #  Hours < 0 or > 23 are invalids.
    if int(hours) < 0 or int(hours) > 23:
        return False
    #  Minutes < 0 or > 59 are invalids.
    if int(minutes) < 0 or int(minutes) > 59:
        return False
    # If there are not 2 digits, is invalid.
    if len(minutes) < 2 or len(hours) < 2:
        return False
    #  Else, is a valid format for the bot.
    return True


def check_o_clock_hours(hour):
    """
    Checks o'clock hours, and creates a correct format, if possible.
    :param hour:
    :return:
    """
    #  If the format contains minutes, goes to check_one_cifre_hours, and returns it.
    if len(hour) > 2:
        one_cifre_check = check_one_cifre_hours(hour)
        return one_cifre_check
    #  If it is not a number, is invalid.
    if not hour.isdigit():
        return False
    #  If it is an hour o'clock (for example 7) returns it in a valid format for the bot.
    if 0 < int(hour) < 10 and len(hour) == 1:
        return "0{}:00".format(hour)
    #  The same with 2 digit hours.
    elif int(hour) < 24:
        return "{}:00".format(hour)
    else:
        return False


def check_one_cifre_hours(hour):
    """
    Check hours that user sent with only one digit, and corrects them if possible.
    :param hour:
    :return:
    """
    if ":" not in hour:
        return False
    #  Separates hours and minutes.
    separated_hours = hour.split(":")
    #  If they aren't numbers, return False.
    if not separated_hours[0].isdigit() or not separated_hours[1].isdigit():
        return False
    #  Is hour is less than ten, corrects it's format, else return False.
    if 0 < int(separated_hours[0]) < 10:
        hours = "0{}".format(format(separated_hours[0]))
    else:
        return False
    #  If minutes is less than 0 or more than 59, return False.
    if not 0 < int(separated_hours[1]) < 60:
        return False
    #  Corrects format if minutes have only one digit.
    if int(separated_hours[1]) < 10:
        separated_hours[1] = "0{}".format(separated_hours[1])
    #  Creates a correct format hour, and return it.
    total_hour = ""
    total_hour += hours
    total_hour += ":"
    total_hour += separated_hours[1]
    return total_hour


def wrong_hour_format_text():
    #  Returns an error message with html format.
    text = "It seems that you have introduced a wrong hour format. Remember:\n\n" \
           "-Format goes from 00 to 23 for hours, and from 00 to 59 for minutes.\n\n" \
           "-It <b>MUST</b> contain two digits (not 5:30, but 05:30) for minutes and hours. \n\n" \
           "-Hours and minutes are separated with <b>':'</b> without any space.\n\n" \
           "Examples: 17:00, 15:15, 06:30, 23:12, 00:00, 09:56 etc\n\n" \
           "Write the command and try again!"
    return text


def calculate_total_day_payment(user: dict):
    """
    Calculates daily payment, receiving a dictionary containing the user information.
    :param user:
    :return:
    """
    #  Saves all the informations that will use.
    pay_per_hour = float(user["payment_per_hour"])
    start_hour = user["arrival_time"]
    exit_hour = user["exit_time"]
    #  Calculate total time that passes between those two hours.
    total_hours = calculate_total_hours(start_hour, exit_hour)
    #  Calculates money.
    total_money = round(total_hours * pay_per_hour, 2)
    #  Returns it.
    return total_money


def calculate_total_hours(start_hour, exit_hour):
    """
    Given an start hour and exit hour, calculates time that passes between one another, in seconds.
    :param start_hour:
    :param exit_hour:
    :return:
    """
    #  Necessary when using database. Not needed if user uses it directly in the chat.
    if type(start_hour) == tuple:
        start_hour = start_hour[0]
    if type(exit_hour) == tuple:
        exit_hour = exit_hour[0]
    #  For end of month functions
    if start_hour is None:
        return 0
    #  Divides hour in hours and minutes.
    start_hour = start_hour.split(":")
    #  Calculates seconds that passed from midnight to that concrete hour.
    total_start_seconds = int(start_hour[0]) * 3600 + int(start_hour[1]) * 60
    #  Still for database.
    if exit_hour is None:
        return 0
    else:
        exit_hour = exit_hour.split(":")
    #  Does the same with exit hour.
    total_exit_seconds = int(exit_hour[0]) * 3600 + int(exit_hour[1]) * 60
    #  If exit seconds are larger than start seconds, all passed in the same day, and returns it's difference.
    if total_exit_seconds > total_start_seconds:
        return round((total_exit_seconds - total_start_seconds) / 3600, 2)
    else:
        #  Otherwise, exit passed after midnight. Does the same.
        return round(((24 * 3600) - total_start_seconds + total_exit_seconds) / 3600, 2)


def calculate_current_day(user_data):
    """
    Given a certain number, from 0 to 6, calculates which day of the week name return.
    :param user_data:
    :return:
    """
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    number_of_day = user_data["work_days"]["number_of_day"]
    day_name = day_list[number_of_day]

    return day_name


def check_if_float_number(number: str):
    """
    Checks if a number is float, and returns it rounded.
    :param number:
    :return:
    """
    try:
        number = float(number)
        return round(number, 2)
    except ValueError:
        return False

def receive_current_day():
    """
    Returns current day, in a format that the bot can use. IMPORTANT! This is modified to have the server in different
    timezone. In this case, an hour less.
    :return:
    """
    current_time = datetime.datetime.now()
    current_hour = datetime.datetime.strptime(receive_current_hour(), "%H:%M").time()
    if current_hour.hour == 0:
        next_day = current_time + datetime.timedelta(days=1)
        return next_day.strftime("%d-%m-%Y")
    else:
        return current_time.strftime("%d-%m-%Y")


def receive_current_hour():
    """
    Returns the current hour plus one hour using datetime library. IMPORTANT! This is modified to have the server in a
    different timezone. In this case, an hour less.
    :return:
    """
    current_hour = datetime.datetime.now()
    current_hour_plus_one = current_hour + datetime.timedelta(hours=1)
    return current_hour_plus_one.strftime("%H:%M")


def check_if_lower_hour(start_hour: str, end_hour: str):
    """
    Return the lower hour between two given hours.
    :param start_hour:
    :param end_hour:
    :return:
    """
    #  Needed when working with database.
    if type(start_hour) == tuple:
        start_hour = start_hour[0]
    if type(end_hour) == tuple:
        end_hour = end_hour[0]
    #  Splits the hours in hours and minutes.
    split_start_hour = start_hour.split(":")
    split_end_hour = end_hour.split(":")
    #  Changes its type to integers.
    start_only_hour = int(split_start_hour[0])
    end_only_hour = int(split_end_hour[0])

    #  Check which hour is lower.
    if start_only_hour < end_only_hour:
        return start_hour
    elif start_only_hour > end_only_hour:
        return end_hour
    #  If they are equal, tries with the minutes.
    else:
        if split_start_hour[1] < split_end_hour[1]:
            return start_hour
        elif split_start_hour[1] > split_end_hour[1]:
            return end_hour
        #  If they are also equal, returns start hour.
        else:
            return start_hour


def get_previous_day():
    """
    Given a current day, returns it's previous.
    :return:
    """
    current_day = datetime.datetime.now()
    previous_day = current_day - datetime.timedelta(days=1)

    return previous_day.strftime("%d-%m-%Y")


def end_month_add_extra_hours_to_days(total_days, usual_hours, free_days_pattern):
    """
    Registers don't have to be always complete. If the user don't use the chat for a day, or more, it will
    suppose that everything went as in the normal work schedule.

    This function receive those incomplete registers from the database, and completes them if needed, and
    then calculates the extra hours.

    :param total_days:
    :param usual_hours:
    :param free_days_pattern:
    :return:
    """

    #  Creates an empty list an a variable at 0.
    days_with_extra_hours = []
    total_extra_hours = 0
    #  Calculate the difference in the normal schedule hours.
    usual_hours_difference = calculate_total_hours(usual_hours[0], usual_hours[1])

    #  Produces a loop for every day in the given total days list.
    for day in total_days:
        #  Calculates which day is a certain date.
        week_day = calculate_what_day_is(day[1])
        #  If that day is a working day.
        if free_days_pattern[week_day]:
            #  Extra hours equals the duration of that work day, minus the normal working time.
            extra_hours = round(calculate_total_hours(day[2], day[3]) - usual_hours_difference, 1)

        #  If it is a free day.
        else:
            #  If there are no registers, user didn't work that day.
            if day[2] is None and day[3] is None:
                extra_hours = 0

            #  If there are, calculates it normally.
            else:
                extra_hours = round(calculate_total_hours(day[2], day[3]), 1)

        #  Add results to total extra hours variable.
        total_extra_hours += extra_hours
        #  Adds it to the list.
        days_with_extra_hours.append([day[0], day[1], day[2], day[3], extra_hours])

    #  Rounds total extra hours, adds it at the end of the list, and return the list.
    total_extra_hours = round(total_extra_hours, 1)
    days_with_extra_hours.append({"total_extra_hours": total_extra_hours})

    return days_with_extra_hours


def calculate_what_day_is(day):
    """
    Given a certain day, calculates which day of the week is.
    :param day:
    :return:
    """
    date = datetime.datetime.strptime(day, '%d-%m-%Y')
    week_day = date.strftime('%A')
    return week_day


def free_days_pattern(free_days):
    """
    Transform free days register from the database, with 0 as False and 1 as True, to a python dictionary.
    :param free_days:
    :return:
    """
    #  Transforms tuple to a list.
    day_list = list(free_days[0])
    #  Removes user telegram id, so it don't get an error while iterating.
    day_list.remove(free_days[0][0])

    #  Creates a default dictionary, with everything at False.
    day_dictionary = {"Monday": False, "Tuesday": False, "Wednesday": False, "Thursday": False,
                      "Friday": False, "Saturday": False, "Sunday": False}

    #  Iterates through the database register, modifying the dictionary when a day is True.
    for i, day in enumerate(day_dictionary):
        if day_list[i] == 1:
            day_dictionary[day] = True

    #  Returns the dictionary.
    return day_dictionary


def create_message_end_of_the_month(total_days, money_per_hour):
    """
    Creates a detailed message to send to the user at the end of the month.
    :param total_days:
    :param money_per_hour:
    :return:
    """

    #  Get the total extra hours from the end of the list.
    total_extra_hours = total_days[-1]
    total_extra_hours = total_extra_hours['total_extra_hours']

    #  Eliminates it from the list, to avoid getting an error while iterating.
    total_days.pop()
    #  Creates an empty message.
    message = ""

    #  Start iterating through every day in total days, and adding information to the empty message.
    for day in total_days:
        #  If there are no register, prints that was a day off.
        if day[2] is None:
            message += "-{}, {} was your day off.\n\n".format(day[1], calculate_what_day_is(day[1]))
        #  if not, creates a message with a detailed schedule that day.
        else:
            message += "-{}, {} you worked from {} to {}, making a total of <b>{} extra hours</b> \n\n".format(
                day[1], calculate_what_day_is(day[1]), day[2], day[3], day[4])

    #  Calculates total money, and adds it to the message.
    total_money = round(total_extra_hours * money_per_hour[0], 2)
    message += "\n\n Total extra hours are {}. Making a total of {}€".format(total_extra_hours, total_money)

    #  Return the message.
    return message


def change_days_to_number(day):
    """
    Given a certain date in a format dd-mm-yyyy, returns only the day.
    :param day:
    :return:
    """
    split_days = day.split("-")
    only_day = split_days[0]
    return int(only_day)


def create_simplified_message(total_days, money_per_hour):
    """
    Creates a simplified message with the extra hours that is easier to read fast, rounds them to half an hour
    (0.5 hours), and sends it to the user.
    :param total_days:
    :param money_per_hour:
    :return:
    """
    #  Eliminates last index in total days.
    total_days.pop()

    #  Starts a total counter and half hour counter, at 0.
    total_counter = 0
    half_hour_counter = 0

    #  Creates an empty message.
    message = ""

    #  Iterates through every day.
    for day in total_days:
        #  Calculates the day.
        day_number = change_days_to_number(day[1])
        #  Calculate the half an hours that day.
        extra_hours = calculate_half_hours(half_hour_counter, day_number, day[4], day[2])
        #  Adds all to the message.
        message += extra_hours[0]
        #  Adds the rest to half hour counter.
        half_hour_counter = extra_hours[1]
        #  Adds the total amount to total counter.
        total_counter += extra_hours[2]

    #  Adds total hours, total money and the minutes not added at the end of the message, and returns it.
    message += "\nTotal = {} hours.\nTotal money = {}€.\n {} minutes not added to the extra hours."\
               .format(total_counter, money_per_hour[0] * total_counter, round(half_hour_counter * 60, 1))
    return message


def calculate_half_hours(counter, day, hours, start_hour):
    """
    Creates simple messages for every day, to be included individually in the big simplified message.
    :param counter:
    :param day:
    :param hours:
    :param start_hour:
    :return:
    """
    #  If it was a day off, adds a big line.
    if start_hour is None:
        message = "<b>-Day {}  -----------------\n\n</b>".format(day)
        complete_hours = 0
    else:
        #  Calculates half hours and rest.
        message = ""
        half_hours = hours // 0.5
        rest = hours % 0.5

        #  Add rest to counter.
        counter += rest
        #  If the counter has exceeded 0.5, adds it to half hours, and rest 0.5 to the counter.
        if counter >= 0.5:
            half_hours += 1
            counter -= 0.5

        #  Calculate complete hours, and adds everything to the message.
        complete_hours = half_hours / 2
        message += "<b>-Day {} - {} hours.</b>\n\n".format(day, complete_hours)

    #  Returns message, counter and complete hours.
    return message, counter, complete_hours


def calculate_how_many_days(date_in_the_same_month):
    """
    Given a certain month, calculates how many days it has.
    :param date_in_the_same_month:
    :return:
    """
    date = datetime.datetime.strptime(date_in_the_same_month, "%d-%m-%Y").date()

    last_day = date.replace(month=date.month + 1, day=1) - datetime.timedelta(days=1)
    month_duration = last_day.day
    return month_duration


def add_all_days(days, free_days, start_hour, finish_hour):
    """
    Given a certain register, fill up with all the remaining days, where the user didn't entered a register.
    :param days:
    :param free_days:
    :param start_hour:
    :param finish_hour:
    :return:
    """
    #  Takes the first day from the tuple.
    first_day = days[0][1]
    #  Calculates month duration for that specific day and month.
    month_duration = calculate_how_many_days(first_day)
    #  Creates an empty list to be returned
    list_to_return = []
    #  Breaks the day string in three pieces: "03" + "12" + "1997"
    day_pattern = first_day.split("-")
    #  Saves month and year, in a correct format: "12-1997"
    month_and_year = day_pattern[1] + "-" + day_pattern[2]
    #  Gets the telegram id from the first day.
    id = days[0][0]
    #  Creates a counter, for days without registries.
    days_list_counter = 0

    #  Iterates over every day of the month.
    for i in range(1, month_duration + 1):
        #  If the given day is not in days list, it adds it automatically, with a correct format.
        if days_list_counter >= len(days) or change_days_to_number(days[days_list_counter][1]) != i:
            if i < 10:
                day = "0{}-".format(i)
            else:
                day = "{}-".format(i)

            #  Creates a complete date adding day plus month and year.
            complete_day = day + month_and_year

            #  If it was a working day, adds it to the list with a start and finish hour.
            if free_days[calculate_what_day_is(complete_day)]:
                list_to_return.append((id, complete_day, start_hour[0], finish_hour[0], None))
            #  If it was a free day, adds it without hours.
            else:
                list_to_return.append((id, complete_day, None, None, None))

        else:
            #  If the day was in the register, completes it and adds it to the list.
            complete_day = complete_days(days[days_list_counter], start_hour, finish_hour)
            list_to_return.append(complete_day)
            days_list_counter += 1

    #  Returns the list.
    return list_to_return


def complete_days(day, start_hour, finish_hour):
    """
    Given a day in the database, completes it if required.
    :param day:
    :param start_hour:
    :param finish_hour:
    :return:
    """
    #  Needed when working with database data.
    if type(start_hour) == tuple:
        start_hour = start_hour[0]
    if type(finish_hour) == tuple:
        finish_hour = finish_hour[0]

    #  If there are not entry hour, completes it.
    if day[2] is None and day[3] is not None:
        return tuple([day[0], day[1], start_hour, day[3], day[4]])
    #  If there are not exit hour, completes it.
    elif day[3] is None and day[2] is not None:
        return tuple([day[0], day[1], day[2], finish_hour, day[4]])
    #  Else, returns it as it is.
    else:
        return day
