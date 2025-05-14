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
@brief   A class to handle all requests to the API, managing caching and rate limiting

@date    5/13/2025
@updated 5/14/2025

@author  Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from enum import Enum
import json
import time
from typing import List, Dict

import requests

from .common_utils import BASE_URL, TOKEN_POSTFIX, GroupMeException, print_time


class ChatType(Enum):
    GROUP = 0
    DM = 1


class Requester:
    def __init__(self, token: str):
        """
        @brief  Constructor
        @param  token (str): The user's token, which will be used in all requests
        """
        self.token = token
        self.chat_cache = {}
        self.message_cache = {}
        self.timeout = 1

    def request(self, endpoint: str, params: Dict | None = None, except_message: str | None = None) -> List | Dict:
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
        response = requests.get(f'{BASE_URL}{endpoint}{TOKEN_POSTFIX}{self.token}', params=params)

        # Check for rate-limiting
        while response.status_code == 429:
            print(f'WARNING! Request blocked due to high request frequency. Waiting {print_time(self.timeout)} and retrying...')
            time.sleep(self.timeout)
            response = requests.get(f'{BASE_URL}{endpoint}{TOKEN_POSTFIX}{self.token}', params=params)
            self.timeout = self.timeout * 2

        # Reset timeout
        self.timeout = 1

        # Check for empty return
        if response.status_code == 304:
            if endpoint.startswith('groups'):
                return {'messages': []}
            elif endpoint == 'direct_messages':
                return {'direct_messages': []}

        # Check for error status code
        if response.status_code != 200:
            raise GroupMeException(f'{except_message}. GroupMe API Error Code: {response.status_code}')
        return json.loads(response.text)['response']

    def cache_chat(self, name: str, chat: Dict):
        """
        @brief  Caches a chat by name so that it's data can be fetched later
        @param  name (str):  The name of the chat
        @param  chat (Dict): Dictionary containing the chat data as returned from the API
        """
        # Cache chat if not already cached
        if name not in self.chat_cache.keys():
            if 'name' in chat.keys():
                chat_type = ChatType.GROUP
            else:
                chat_type = ChatType.DM
            self.chat_cache[name] = (chat_type, chat)

    def cache_message(self, chat_id: str, msg_id: str, message: Dict, is_group: bool):
        """
        @brief  Caches a message by ID so that it's data can be fetched later
        @param  chat_id (str):  The ID of the chat in which the message was sent (group ID or DM recipient user ID)
        @param  msg_id  (str):  The ID of the message to cache
        @param  message (Dict): Dictionary containing the message data as returned from the API
        @param  is_group (bool): If the chat is a group (as opposed to a DM)
        """
        # Construct cache entry ID
        chat_type = 'G' if is_group else 'D'
        msg_id = f'{chat_type}_{chat_id}_{msg_id}'

        # Cache message if not already cached
        if msg_id not in self.message_cache.keys():
            self.message_cache[msg_id] = message

    def request_chat(self, chat_name: str, is_group: bool) -> (ChatType, Dict):
        """
        @brief  Fetches a chat's data from the cache using its ID, or requests it from the API in the case of a cache miss
        @param  chat_name (str):  The chat's name
        @param  is_group  (bool): If the chat is a group (as opposed to a DM)
        @return: (Dict) The chat's data as returned from the API
        """
        if chat_name in self.chat_cache.keys():
            return self.chat_cache[chat_name]
        else:
            chat = self.get_chat_by_name(chat_name, is_group)
            self.cache_chat(chat_name, chat)
            chat_type = ChatType.GROUP if is_group else ChatType.DM
            return chat_type, chat

    def request_message(self, msg_id: str) -> Dict:
        """
        @brief  Fetches a message's data from the cache, or requests it from the API in the case of a cache miss
        @param  msg_id    (str):  The message's fully qualified cache entry ID (X_YYY_ZZZ), where
         - X is "G" if the message was sent in a group or "D" if the message was a DM
         - YYY is the ID of the chat
         - ZZZ is the ID of the message
        @return: (Dict) The message's data as returned by the API
        """
        if msg_id in self.message_cache.keys():
            return self.message_cache[msg_id]
        else:
            chat_type, chat_id, msg_id = msg_id.split('_')
            is_group = chat_type == 'G'
            message = self.get_message_by_id(chat_id, msg_id, is_group)
            self.cache_message(chat_id, msg_id, message, is_group)
            return message

    def get_chat_by_name(self, chat_name: str, is_group: bool) -> Dict | None:
        """
        @brief  Gets a chat's data from the API
        @param  chat_name (str): The name of the chat
        @return (Dict) The chat's data as returned by the API
        """
        # Get chats
        url = 'groups' if is_group else 'chats'
        params = {
            'page': 1,
            'per_page': 10
        }
        if is_group:
            params['omit'] = 'memberships'

        # Loop through chats
        chat_page = self.request(url, params, 'Unexpected error searching chats')
        while len(chat_page) > 0:
            # Loop over page
            for i, chat in enumerate(chat_page):
                if is_group:
                    curr_chat_name = chat['name']
                else:
                    curr_chat_name = chat['other_user']['name']
                if curr_chat_name == chat_name:
                    return chat

            # Get next page
            params['page'] = params['page'] + 1
            chat_page = self.request(url, params, 'Unexpected error searching chats')

        return None

    def get_message_by_id(self, chat_id: str, msg_id: str, is_group: bool) -> Dict:
        """
        @brief  Fetches a message's data from the API
        @param  chat_id   (str):  The ID of the chat containing the message
        @param  msg_id    (str):  The ID of the message
        @param  is_group: (bool): If the message is from a group (as opposed to a DM)
        @return: (Dict) The message's data as returned by the API
        """
        # Set initial parameters
        params = {
            'before_id': msg_id,
            'limit': 1
        }

        # Set endpoint
        if is_group:
            endpoint = f'groups/{chat_id}/messages'
            message_list_key = 'messages'
        else:
            endpoint = 'direct_messages'
            params['other_user_id'] = chat_id
            message_list_key = 'direct_messages'

        # Get ID of message prior to message to be fetched
        try:
            prev_msg_id = self.request(endpoint, params)[message_list_key][0]['id']

            # Get message immediately after (this is the desired message)
            del params['before_id']
            params['after_id'] = prev_msg_id
            return self.request(endpoint, params)[message_list_key][0]
        except IndexError:
            # There is no message before the desired message (it is the first message in the group)
            # Get message immediately after desired message
            del params['before_id']
            params['after_id'] = msg_id
            try:
                after_msg_id = self.request(endpoint, params)[message_list_key][0]['id']

                # Get message immediately before (this is the desired message)
                del params['after_id']
                params['before_id'] = after_msg_id
                return self.request(endpoint, params)[message_list_key][0]
            except IndexError:
                # There is only one message in the group
                return self.request(endpoint)[message_list_key][0]
