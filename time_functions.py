"""
@package groupme
@brief   Helper functions to manipulate time objects

@date    6/1/2024
@updated 7/20/2024

@author Preston Buterbaugh
"""
# Imports
from datetime import datetime
import time

from common_utils import GroupMeException


def to_seconds(number: int, units: str) -> int:
    """
    @brief Converts a given number with given units to seconds
    @param number (int): The number to convert to seconds
    @param units (str): The units
        - "min" - Minutes
        - "h" - Hours
        - "d" - Days
        - "w" - Weeks
        - "m" - Months
        - "y" - Days
    @return (int) The number of seconds
    """
    if units == 'min':
        return number * 60
    elif units == 'h':
        return number * 3600
    elif units == 'd':
        return number * 3600 * 24
    elif units == 'w':
        return number * 3600 * 24 * 7
    elif units == 'm':
        curr_time = time.localtime(time.time())
        month = curr_time.tm_mon
        year = curr_time.tm_year
        months_to_subtract = number % 12
        years_to_subtract = number // 12
        cutoff_date = datetime(year - years_to_subtract, month - months_to_subtract, curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec)
        return int(time.time() - cutoff_date.timestamp())
    elif units == 'y':
        curr_time = time.localtime(time.time())
        year = curr_time.tm_year
        cutoff_date = datetime(year - number, curr_time.tm_mon, curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec)
        return int(time.time() - cutoff_date.timestamp())
    else:
        raise GroupMeException('Invalid units specified for last_used duration')


def to_twelve_hour_time(hour: int, minute: int, second: int) -> str:
    """
    @brief Converts 24 hour time to 12 hour time
    @param hour    (int): The hour in 24-hour time
    @param minute  (int): The minute
    @param second  (int): The second
    @return (str) The time in 12-hour time formatted as hh:mm:ss a
    """
    # Normalize hour
    if hour > 23:
        hour = hour % 24

    if hour == 0:
        return f'12:{str(minute).zfill(2)}:{str(second).zfill(2)} AM'
    elif hour < 12:
        return f'{hour}:{str(minute).zfill(2)}:{str(second).zfill(2)} AM'
    elif hour == 12:
        return f'12:{str(minute).zfill(2)}:{str(second).zfill(2)} PM'
    else:
        return f'{hour - 12}:{str(minute).zfill(2)}:{str(second).zfill(2)} PM'


def string_to_epoch(time_string: str) -> int:
    """
    @brief Converts a date/time string formatted as "MM/dd/yyyy" or "MM/dd/yyyy" to seconds since epoch
    @param time_string (str): The date or time string
    @return (int): The number of seconds since epoch
    """
    # Split into date and time components
    components = time_string.split(' ')
    if len(components) > 2:
        raise GroupMeException('Time strings must be formatted as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss"')

    date_component = components[0]
    if len(components) == 2:
        time_component = components[1]
    else:
        time_component = '00:00:00'

    # Split components into numbers
    date_numbers = date_component.split('/')
    if len(date_numbers) != 3:
        raise GroupMeException('Improperly formatted date. Must be formatted as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss"')
    try:
        month = int(date_numbers[0])
        day = int(date_numbers[1])
        year = int(date_numbers[2])
    except ValueError:
        raise GroupMeException('Invalid numeric values provided for date. Must be formatted as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss"')

    time_numbers = time_component.split(':')
    if len(time_numbers) != 3:
        raise GroupMeException('Improperly formatted date. Must be formatted as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss"')
    try:
        hour = int(time_numbers[0])
        minute = int(time_numbers[1])
        second = int(time_numbers[2])
    except ValueError:
        raise GroupMeException('Invalid numeric values provided for time. Must be formatted as "MM/dd/yyy" or "MM/dd/yyyy hh:mm:ss"')

    # Convert to epoch time
    return int(datetime(year, month, day, hour, minute, second).timestamp())


def epoch_to_string(epoch: int) -> str:
    """
    @brief  Converts a point in time expressed as seconds from epoch to a string
    @param  epoch (int): A point in time specified in seconds from epoch
    @return (str) A string representation of the point in time
    """
    time_obj = time.localtime(epoch)
    return f'{time_obj.tm_mon}/{time_obj.tm_mday}/{time_obj.tm_year} {to_twelve_hour_time(time_obj.tm_hour, time_obj.tm_min, time_obj.tm_sec)}'


def epoch_to_month_year(epoch: int) -> str:
    """
    @brief  Converts a point in time expressed as seconds from epoch to a string formatted as MMMMM yyyy
    @param  epoch (int): A point in time specified in seconds from epoch
    @return (str) A string representation of the point in time
    """
    time_obj = time.localtime(epoch)
    return f'{month_name(time_obj.tm_mon)} {time_obj.tm_year}'


def month_name(month_num: int) -> str:
    """
    @brief  Gets the name of a month from its number
    @param  month_num (int): A month represented as a number (1-12)
    @return (str) The name of the month
    """
    if month_num == 1:
        return 'January'
    elif month_num == 2:
        return 'February'
    elif month_num == 3:
        return 'March'
    elif month_num == 4:
        return 'April'
    elif month_num == 5:
        return 'May'
    elif month_num == 6:
        return 'June'
    elif month_num == 7:
        return 'July'
    elif month_num == 8:
        return 'August'
    elif month_num == 9:
        return 'September'
    elif month_num == 10:
        return 'October'
    elif month_num == 11:
        return 'November'
    elif month_num == 12:
        return 'December'
