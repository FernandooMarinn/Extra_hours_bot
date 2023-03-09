import datetime




def check_hour(hour):
    if hour == False:
        return False

    if ":" not in hour:
        return False

    divided_hour = hour.split(":")

    hours = divided_hour[0]
    minutes = divided_hour[1]

    if not hours.isdigit() or not minutes.isdigit():
        return False

    if int(hours) < 0 or int(hours) > 23:
        return False
    if int(minutes) < 0 or int(minutes) > 59:
        return False

    if len(minutes) < 2 or len(hours) < 2:
        return False

    return True


def check_o_clock_hours(hour):
    if len(hour) > 2:
        one_cifre_check = check_one_cifre_hours(hour)
        return one_cifre_check

    if not hour.isdigit():
        return False

    if 0 < int(hour) < 10 and len(hour) == 1:
        return "0{}:00".format(hour)
    elif int(hour) < 24:
        return "{}:00".format(hour)
    else:
        return False


def check_one_cifre_hours(hour):
    if not ":" in hour:
        return False

    separated_hours = hour.split(":")
    try:
        int(separated_hours[0])
        int(separated_hours[1])
    except ValueError:
        return False
    if 0 < int(separated_hours[0]) < 10:
        hours = "0{}".format(format(separated_hours[0]))
    else:
        return False
    if not 0 < int(separated_hours[1]) < 60:
        return False
    total_hour = ""
    total_hour += hours
    total_hour += ":"
    total_hour += separated_hours[1]
    return total_hour



def wrong_hour_format_text():
    text = "It seems that you have introduced a wrong hour format. Remember:\n\n" \
           "-Format goes from 00 to 23 for hours, and from 00 to 59 for minutes.\n\n" \
           "-It <b>MUST</b> contain two digits (not 5:30, but 05:30) for minutes and hours. \n\n" \
           "-Hours and minutes are separated with <b>':'</b> without any space.\n\n" \
           "Examples: 17:00, 15:15, 06:30, 23:12, 00:00, 09:56 etc\n\n" \
           "Write the command and try again!"
    return text


def calculate_total_day_payment(user: dict):
    pay_per_hour = float(user["payment_per_hour"])
    start_hour = user["arrival_time"]
    exit_hour = user["exit_time"]

    total_hours = calculate_total_hours(start_hour, exit_hour)

    total_money = round(total_hours * pay_per_hour, 2)

    return total_money


def calculate_total_hours(start_hour, exit_hour):
    if type(start_hour) == tuple:
        start_hour = start_hour[0]
        exit_hour = exit_hour[0]
    #  For end of month functions
    if start_hour is None:
        return 0
    start_hour = start_hour.split(":")

    total_start_seconds = int(start_hour[0]) * 3600 + int(start_hour[1]) * 60

    exit_hour = exit_hour.split(":")

    total_exit_seconds = int(exit_hour[0]) * 3600 + int(exit_hour[1]) * 60

    if total_exit_seconds > total_start_seconds:
        return round((total_exit_seconds - total_start_seconds) / 3600, 1)
    else:

        return round(((24 * 3600) - total_start_seconds + total_exit_seconds) / 3600, 1)


def calculate_current_day(user_data):
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    number_of_day = user_data["work_days"]["number_of_day"]
    day_name = day_list[number_of_day]

    return day_name


def check_if_float_number(number):
    try:
        float(number)
        return round(float(number), 2)
    except ValueError:
        return False


def recieve_current_day():
    """
    Returns the current day using datetime library.
    :return:
    """
    day = datetime.date.today().strftime("%d-%m-%Y")
    return day


def recieve_current_hour():
    """
    Returns the current hour using datetime library.
    :return:
    """
    current_hour = datetime.datetime.now().strftime("%H:%M")
    return current_hour


def check_if_lower_hour(start_hour: str, end_hour: str):
    """
    Return the lower hour between two options.
    :param start_hour:
    :param end_hour:
    :return:
    """
    split_start_hour = start_hour.split(":")
    split_end_hour = end_hour.split(":")

    start_only_hour = int(split_start_hour[0])
    end_only_hour = int(split_end_hour[0])

    if start_only_hour < end_only_hour:
        return start_hour
    elif start_only_hour > end_only_hour:
        return end_hour
    else:
        if split_start_hour[1] < split_end_hour[1]:
            return start_hour
        elif split_start_hour[1] > split_end_hour[1]:
            return end_hour
        else:
            return start_hour


def get_previous_day():
    current_day = datetime.datetime.now()
    previous_day = current_day - datetime.timedelta(days=1)

    return previous_day.strftime("%d-%m-%Y")


def end_month_add_extra_hours_to_days(total_days, usual_hours, free_days_pattern):
    days_with_extra_hours = []
    total_extra_hours = 0

    usual_hours_difference = calculate_total_hours(usual_hours[0], usual_hours[1])

    for day in total_days:
        week_day = calculate_what_day_is(day[1])
        if free_days_pattern[week_day]:
            extra_hours = round(calculate_total_hours(day[2], day[3]) - usual_hours_difference, 1)
        else:
            if day[2] is None:
                extra_hours = 0
            else:
                extra_hours = round(calculate_total_hours(day[2], day[3]), 1)
        total_extra_hours += extra_hours
        days_with_extra_hours.append([day[0], day[1], day[2], day[3], extra_hours])

    total_extra_hours = round(total_extra_hours, 1)
    days_with_extra_hours.append({"total_extra_hours": total_extra_hours})

    return days_with_extra_hours


def calculate_what_day_is(day):
    date = datetime.datetime.strptime(day, '%d-%m-%Y')
    week_day = date.strftime('%A')
    return week_day


def free_days_pattern(free_days):
    day_list = list(free_days[0])
    day_list.remove(free_days[0][0])

    day_dictionary = {"Monday": False, "Tuesday": False, "Wednesday": False, "Thursday": False,
                      "Friday": False, "Saturday": False, "Sunday": False}
    for i, day in enumerate(day_dictionary):
        if day_list[i] == 1:
            day_dictionary[day] = True

    return day_dictionary


def create_message_end_of_the_month(total_days, money_per_hour):
    total_extra_hours = total_days[-1]
    total_extra_hours = total_extra_hours['total_extra_hours']

    total_days.pop()
    message = ""
    for day in total_days:
        if day[2] is None:
            message += "-{}, {} was your day off.\n\n".format(day[1], calculate_what_day_is(day[1]))
        else:
            message += "-{}, {} you worked from {} to {}, making a total of <b>{} extra hours</b> \n\n".format(
                day[1], calculate_what_day_is(day[1]), day[2], day[3], day[4])
    total_money = round(total_extra_hours * money_per_hour[0], 2)
    message += "\n\n Total extra hours are {}. Making a total of {}€".format(total_extra_hours, total_money)

    return message


def change_days_to_number(day):
    split_days = day.split("-")
    only_day = split_days[0]
    return int(only_day)


def create_simplified_message(total_days, money_per_hour):
    total_days.pop()
    total_counter = 0
    half_hour_counter = 0
    message = ""
    for day in total_days:
        day_number = change_days_to_number(day[1])
        extra_hours = calculate_half_hours(half_hour_counter, day_number, day[4], day[2])
        message += extra_hours[0]
        half_hour_counter = extra_hours[1]
        total_counter += extra_hours[2]

    message += "\nTotal = {} hours.\nTotal money = {}€.\n {} minutes not added to the extra hours."\
               .format(total_counter, money_per_hour[0] * total_counter, round(half_hour_counter * 60, 1))
    return message


def calculate_half_hours(counter, day, hours, start_hour):
    if start_hour is None:
        message = "<b>-Day {}  -----------------\n\n</b>".format(day)
        complete_hours = 0
    else:
        message = ""
        half_hours = hours // 0.5
        rest = hours % 0.5

        counter += rest
        if counter >= 0.5:
            half_hours += 1
            counter -= 0.5

        complete_hours = half_hours / 2
        message += "<b>-Day {} - {} hours.</b>\n\n".format(day, complete_hours)
    return message, counter, complete_hours


def calculate_how_many_days(date_in_the_same_month):
    date = datetime.datetime.strptime(date_in_the_same_month, "%d-%m-%Y").date()

    last_day = date.replace(month=date.month + 1, day=1) - datetime.timedelta(days=1)
    month_duration = last_day.day
    return month_duration


def add_all_days(days, free_days, start_hour, finish_hour):
    first_day = days[0][1]
    month_duration = calculate_how_many_days(first_day)
    list_to_return = []

    day_pattern = first_day.split("-")
    month_and_year = day_pattern[1] + "-" + day_pattern[2]

    id = days[0][0]

    days_list_counter = 0
    for i in range(1, month_duration + 1):
        if days_list_counter >= len(days) or change_days_to_number(days[days_list_counter][1]) != i:
            if i < 10:
                day = "0{}-".format(i)
            else:
                day = "{}-".format(i)
            complete_day = day + month_and_year

            if free_days[calculate_what_day_is(complete_day)]:
                list_to_return.append((id, complete_day, start_hour[0], finish_hour[0], None))
            else:
                list_to_return.append((id, complete_day, None, None, None))
        else:
            list_to_return.append(days[days_list_counter])
            days_list_counter += 1

    return list_to_return

