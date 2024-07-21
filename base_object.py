"""
@package groupme
@brief   A Python object implementation of the GroupMe API

@date    6/1/2024
@updated 7/20/2024

@author  Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from datetime import datetime
import json
import requests
from typing import List
import time

from chat import Chat, Group, DirectMessage
from common_utils import BASE_URL, TOKEN_POSTFIX, call_api, GroupMeException
from time_functions import to_seconds, string_to_epoch


class GroupMe:
    def __init__(self, token: str):
        """
        @brief Constructor
        @param token (str): The user's GroupMe API access token
        """
        url = f'{BASE_URL}users/me{TOKEN_POSTFIX}{token}'
        response = requests.get(url)
        if response.status_code != 200:
            raise GroupMeException('Invalid access token')
        user_info = json.loads(response.text)['response']
        self.token = token
        self.name = user_info['name']
        self.email = user_info['email']
        self.phone_number = user_info['phone_number']

    def _get_group(self, group_name: str) -> Group | None:
        """
        @brief  Gets a group by the specified name
        @param  group_name (str): The name of the group
        @return (Group) An object representing the group
        """
        # Get groups
        url = 'groups'
        params = {
            'page': 1,
            'per_page': 10,
            'omit': 'memberships'
        }

        # Loop through groups
        group_page = call_api(url, self.token, params, 'Unexpected error searching groups')
        while len(group_page) > 0:
            # Loop over page
            for i, group in enumerate(group_page):
                if group['name'] == group_name:
                    return Group(group, self.token)

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, self.token, params, 'Unexpected error searching groups')

        return None

    def _get_dm(self, user_name: str) -> DirectMessage | None:
        """
        @brief  Gets a group by the specified name
        @param  user_name (str): The name of the other user of the direct message
        @return (DirectMessage) An object representing the direct message chat
        """
        # Get groups
        url = 'chats'
        params = {
            'page': 1,
            'per_page': 10
        }

        # Loop through groups
        dm_page = call_api(url, self.token, params, 'Unexpected error searching direct messages')
        while len(dm_page) > 0:
            # Loop over page
            for dm in dm_page:
                if dm['other_user']['name'] == user_name:
                    return DirectMessage(dm)

            # Get next page
            params['page'] = params['page'] + 1
            dm_page = call_api(url, self.token, params, 'Unexpected error searching direct messages')

        return None

    def get_chat(self, chat_name: str, is_dm: bool = False) -> Chat:
        """
        @brief Returns an object for a chat
        @param chat_name (str): The name of the chat to return
        @param is_dm (bool): Performance enhancing flag to specify that the desired chat is a direct message
                             if false, search begins with groups (as opposed to DMs), which can be time-consuming
                             if the user has a lot of groups
        @return (Chat) A GroupMe chat object
        """
        if is_dm:
            chat = self._get_dm(chat_name)
        else:
            chat = self._get_group(chat_name)
            if chat is None:
                chat = self._get_dm(chat_name)

        if chat is None:
            raise GroupMeException(f'No chat found with the name {chat_name}')
        return chat

    def get_chats(self, last_used: str = '', verbose: bool = False) -> List:
        """
        @brief Returns a list of all the user's chats
        @param last_used (str): String specifying how recently the chat should have been used. If empty, all groups are fetched
        @param verbose (bool): If output should be printed showing progress
        @return (List) A list of GroupMe Chat objects
        """
        groups = []
        direct_messages = []
        chats = []

        # Determine cutoff (if applicable)
        cutoff = get_cutoff(last_used)

        # Get groups
        url = f'groups'
        params = {
            'page': 1,
            'per_page': 10,
            'omit': 'memberships'
        }

        # Loop through all group pages
        group_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching groups')
        in_range = True
        num_groups = 0
        while len(group_page) > 0 and in_range:
            # Loop over page
            for i, group in enumerate(group_page):
                # Check last sent message
                if cutoff:
                    last_sent_message = group['messages']['last_message_created_at']
                    if last_sent_message < cutoff:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    num_groups = num_groups + 1
                    print(f'\rFetching groups ({num_groups} retrieved)...', end='')

                # Add to list of groups
                groups.append(Group(group, self.token))

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching groups')

        if verbose:
            print(f'\rFetched {num_groups} groups')

        # Get direct messages
        url = f'chats'
        params = {
            'page': 1,
            'per_page': 10
        }

        # Loop through all direct message pages
        dm_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching direct messages')
        in_range = True
        num_chats = 0
        while len(dm_page) > 0 and in_range:
            # Loop over page
            for i, dm in enumerate(dm_page):
                # Check last sent message
                if cutoff:
                    last_sent_message = dm['last_message']['created_at']
                    if last_sent_message < cutoff:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    num_chats = num_chats + 1
                    print(f'\rFetching direct messages ({num_chats} retrieved)...', end='')

                # Add to list of groups
                direct_messages.append(DirectMessage(dm))

            # Get next page
            params['page'] = params['page'] + 1
            dm_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching direct messages')

        if verbose:
            print(f'\rFetched {num_chats} direct messages')

        # Merge lists
        group_index = 0
        dm_index = 0
        while group_index < len(groups) and dm_index < len(direct_messages):
            if groups[group_index].last_used_epoch > direct_messages[dm_index].last_used_epoch:
                chats.append(groups[group_index])
                group_index = group_index + 1
            else:
                chats.append(direct_messages[dm_index])
                dm_index = dm_index + 1
        if group_index == len(groups):
            while dm_index < len(direct_messages):
                chats.append(direct_messages[dm_index])
                dm_index = dm_index + 1
        else:
            while group_index < len(groups):
                chats.append(groups[group_index])
                group_index = group_index + 1

        return chats

    def get_messages(self, output_file: str = '', before: str = '', after: str = '', keyword: str = '', limit: int = -1, suppress_warning: bool = False) -> List:
        """
        @brief Searches for messages meeting the given criteria
        @param output_file      (str):  The name of a file into which to direct the output. If blank, no output is provided
                                        if specified as "console", it will output to the console
        @param before           (str):  A date string formatted either as "MM/dd/yyyy or MM/dd/yyyy hh:mm:ss" indicating the
                                        time before which messages should have been sent
        @param after            (str):  A date string formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss" indicating the
                                        time after which messages should have been sent
        @param keyword          (str):  A string of text which messages should contain
        @param suppress_warning (bool): If very few parameters are specified, and the search is expected to return a lot
                                        of results, a prompt is displayed by default requiring the user to confirm the
                                        search. Specifying this parameter as true bypasses this prompt, and immediately
                                        proceeds with the search
        @return (List) A list of the message objects returned by the search
        """
        if before != '':
            before = string_to_epoch(before)
        if after != '':
            after = string_to_epoch(after)
        return []


def get_cutoff(last_used: str) -> int | None:
    if last_used == '':
        return None

    date_components = last_used.split('/')
    if len(date_components) == 1:
        # If specified as duration
        number = last_used[0:len(last_used) - 1]
        unit = last_used[len(last_used) - 1]
        try:
            number = int(number)
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = to_seconds(number, unit)
    elif len(date_components) == 3:
        # If specified as date
        try:
            month = int(date_components[0])
            day = int(date_components[1])
            year = int(date_components[2])
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = time.time() - float(datetime(year, month, day).timestamp())
    else:
        raise GroupMeException('Invalid argument for argument "last_used"')
    return int(time.time() - timespan)
