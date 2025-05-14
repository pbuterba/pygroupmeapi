# Copyright (C) 2025 Preston Buterbaugh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/.

"""
@package pygroupmeapi
@brief   General purpose utilities for the GroupMe API

@date    6/1/2024
@updated 5/13/2025

@author Preston Buterbaugh
"""
# Imports
import math

# Global variables
BASE_URL = 'https://api.groupme.com/v3/'
TOKEN_POSTFIX = '?token='


def progress_bar(completed: int, total: int) -> str:
    """
    @brief  Returns a 50 tick progress bar based on a completed number of items and total number of items to complete
    @param  completed (int): The number of items that have been completed:
    @param  total     (int): The total number of items to be completed
    @return (str) A 50 tick ASCII progress bar
    """
    progress = completed/total
    ticks = math.floor((progress * 100)/2)
    dashes = '-' * (50 - ticks)
    ticks = '=' * ticks
    percent_display = f'{round(progress * 100)}%'
    return f' {ticks}{dashes} {percent_display}'


def print_time(seconds: int) -> str:
    """
    @brief  Prints a time in hours, minutes, and seconds with units included
    @param  seconds (int): The total number of seconds
    @return (str) The time printed in hours, minutes, and seconds with units
    """
    # Calculate hours
    hours = seconds // 3600
    seconds = seconds - (hours * 3600)

    # Calculate minutes
    minutes = seconds // 60
    seconds = seconds - (minutes * 60)

    output_string = ''

    # Output hours
    if hours > 0:
        output_string = f'{hours} hour'
        if hours > 1:
            output_string = f'{output_string}s'
        if minutes > 0 or seconds > 0:
            output_string = f'{output_string} '
        if hours > 0 and seconds == 0:
            output_string = f'{output_string}and '

    # Output minutes
    if minutes > 0:
        output_string = f'{output_string}{minutes} minute'
        if minutes > 1:
            output_string = f'{output_string}s'
        if seconds > 0:
            output_string = f'{output_string} and '

    # Output seconds
    if seconds > 0:
        output_string = f'{output_string}{seconds} second'
    if seconds > 1:
        output_string = f'{output_string}s'

    return output_string


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass
