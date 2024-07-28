"""
@package groupme
@brief   General purpose utilities for the GroupMe API

@date    6/1/2024
@updated 7/27/2024

@author Preston Buterbaugh
"""
# Imports
import json
import math
import requests
from typing import List, Dict

# Global variables
BASE_URL = 'https://api.groupme.com/v3/'
TOKEN_POSTFIX = '?token='


def call_api(endpoint: str, token: str, params: Dict | None = None, except_message: str | None = None) -> List | Dict:
    """
    @brief Makes a get call to the API, handles errors, and returns extracted data
    @param  endpoint (str): The API endpoint to which to send the API request
    @param  token (str): The GroupMe access token
    @param  params (Dict): Parameters to pass into the request
    @param  except_message (str): A message to output if API call fails
    @return:
    """
    # Handle optional parameter
    if params is None:
        params = {}
    if except_message is None:
        except_message = 'Unspecified error occurred'

    # Make API call
    response = requests.get(f'{BASE_URL}{endpoint}{TOKEN_POSTFIX}{token}', params=params)
    if response.status_code == 304:
        if endpoint.startswith('groups'):
            return {'messages': []}
        elif endpoint == 'direct_messages':
            return {'direct_messages': []}
    if response.status_code != 200:
        raise GroupMeException(except_message)
    return json.loads(response.text)['response']


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


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass
