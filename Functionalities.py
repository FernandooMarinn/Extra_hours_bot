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


print(check_one_cifre_hours("7:30"))

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
        return round(number, 2)
    except ValueError:
        return False

