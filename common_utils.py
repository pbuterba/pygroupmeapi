"""
@package groupme
@brief   General purpose utilities for the GroupMe API

@date    6/1/2024
@updated 7/23/2024

@author Preston Buterbaugh
"""
# Imports
import json
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
    if response.status_code != 200:
        raise GroupMeException(except_message)
    return json.loads(response.text)['response']


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass
