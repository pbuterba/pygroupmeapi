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
@package groupme
@brief   A Python object implementation of the GroupMe API

@date    6/1/2024
@updated 12/31/2024

@author  Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from datetime import datetime
import json
import math
import requests
import time
from typing import List

from groupme.chat import Chat, Group, DirectMessage
from groupme.common_utils import BASE_URL, TOKEN_POSTFIX, call_api, progress_bar, GroupMeException
from groupme.time_functions import to_seconds


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

    def _get_group(self, group_name: str, timeout: int) -> Group | None:
        """
        @brief  Gets a group by the specified name
        @param  group_name (str): The name of the group
        @param  timeout    (int): The number of seconds to wait before retrying an API call if a 429 error is received
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
        group_page = call_api(url, self.token, params, timeout, 'Unexpected error searching groups')
        while len(group_page) > 0:
            # Loop over page
            for i, group in enumerate(group_page):
                if group['name'] == group_name:
                    return Group(group, self.token)

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, self.token, params, timeout, 'Unexpected error searching groups')

        return None

    def _get_dm(self, user_name: str, timeout: int) -> DirectMessage | None:
        """
        @brief  Gets a group by the specified name
        @param  user_name (str): The name of the other user of the direct message
        @param  timeout   (int): The number of seconds to wait before retrying an API call if a 429 error is received
        @return (DirectMessage) An object representing the direct message chat
        """
        # Get groups
        url = 'chats'
        params = {
            'page': 1,
            'per_page': 10
        }

        # Loop through groups
        dm_page = call_api(url, self.token, params, timeout, 'Unexpected error searching direct messages')
        while len(dm_page) > 0:
            # Loop over page
            for dm in dm_page:
                if dm['other_user']['name'] == user_name:
                    return DirectMessage(dm, self.token)

            # Get next page
            params['page'] = params['page'] + 1
            dm_page = call_api(url, self.token, params, timeout, 'Unexpected error searching direct messages')

        return None

    def get_chat(self, chat_name: str, timeout: int = 1, is_dm: bool = False) -> Chat:
        """
        @brief Returns an object for a chat
        @param chat_name (str): The name of the chat to return
        @param timeout   (int): The number of seconds to wait before retrying an API call if a 429 error is received
        @param is_dm (bool): Performance enhancing flag to specify that the desired chat is a direct message
                             if false, search begins with groups (as opposed to DMs), which can be time-consuming
                             if the user has a lot of groups
        @return (Chat) A GroupMe chat object
        """
        if is_dm:
            chat = self._get_dm(chat_name, timeout)
        else:
            chat = self._get_group(chat_name, timeout)
            if chat is None:
                chat = self._get_dm(chat_name, timeout)

        if chat is None:
            raise GroupMeException(f'No chat found with the name {chat_name}')
        return chat

    def get_chats(self, used_after: str = '', created_before: str = '', timeout: int = 1, verbose: bool = False) -> List:
        """
        @brief Returns a list of all the user's chats
        @param used_after     (str): String specifying how recently the chat should have been used. If empty, all groups are fetched
        @param created_before (str): String specifying a minimum age (in time) or a date before which a chat must have been created
                                     to be included. If empty, groups are fetched regardless of creation time
        @param timeout        (int): The number of seconds to wait before retrying an API call if a 429 error is received
        @param verbose        (bool): If output should be printed showing progress
        @return (List) A list of GroupMe Chat objects
        """
        groups = []
        direct_messages = []
        chats = []

        # Determine cutoffs (if applicable)
        earliest_last_used_time = get_cutoff(used_after)
        min_age = get_cutoff(created_before, '23:59:59')

        # Get groups
        url = f'groups'
        params = {
            'page': 1,
            'per_page': 10,
            'omit': 'memberships'
        }

        # Loop through all group pages
        group_page = call_api(url, self.token, params=params, timeout=timeout, except_message='Unexpected error fetching groups')
        in_range = True
        num_groups = 0
        num_skipped = 0
        while len(group_page) > 0 and in_range:
            # Loop over page
            for i, group in enumerate(group_page):
                # Check creation date
                if min_age:
                    chat_creation_date = group['created_at']
                    if chat_creation_date > min_age:
                        # Handle output if necessary
                        if verbose:
                            num_skipped = num_skipped + 1
                            if num_groups:
                                print(f'\rFetching groups ({num_groups} retrieved, {num_skipped} skipped)...', end='')
                            else:
                                print(f'\rFetching groups ({num_skipped} skipped)...', end='')

                        # Continue to next group
                        continue

                # Check last sent message
                if earliest_last_used_time:
                    last_sent_message = group['messages']['last_message_created_at']
                    if last_sent_message < earliest_last_used_time:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    num_groups = num_groups + 1
                    if num_skipped:
                        print(f'\rFetching groups ({num_groups} retrieved, {num_skipped} skipped)...', end='')
                    else:
                        print(f'\rFetching groups ({num_groups} retrieved)...', end='')

                # Add to list of groups
                groups.append(Group(group, self.token))

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching groups')

        # Finish output
        if verbose:
            if num_groups and num_skipped:
                print(f'\rFetched {num_groups} groups. {num_skipped} skipped because they were created after the specified time')
            elif num_skipped:
                print(f'\rNo groups found matching the specified criteria ({num_skipped} checked)')
            else:
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
        num_skipped = 0
        while len(dm_page) > 0 and in_range:
            # Loop over page
            for i, dm in enumerate(dm_page):
                # Check creation date
                if min_age:
                    first_dm_date = dm['created_at']
                    if first_dm_date > min_age:
                        # Handle output if necessary
                        if verbose:
                            num_skipped = num_skipped + 1
                            if num_chats:
                                print(f'\rFetching direct messages ({num_chats} retrieved, {num_skipped} skipped)...', end='')
                            else:
                                print(f'\rFetching groups ({num_skipped} skipped)...', end='')

                        # Continue to next DM
                        continue

                # Check last sent message
                if earliest_last_used_time:
                    last_sent_message = dm['last_message']['created_at']
                    if last_sent_message < earliest_last_used_time:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    num_chats = num_chats + 1
                    if num_skipped:
                        print(f'\rFetching direct messages ({num_chats} retrieved, {num_skipped} skipped)...', end='')
                    else:
                        print(f'\rFetching direct messages ({num_chats} retrieved)...', end='')

                # Add to list of groups
                direct_messages.append(DirectMessage(dm, self.token))

            # Get next page
            params['page'] = params['page'] + 1
            dm_page = call_api(url, self.token, params=params, except_message='Unexpected error fetching direct messages')

        if verbose:
            # Finish output
            if verbose:
                if num_chats and num_skipped:
                    print(f'\rFetched {num_chats} direct messages. {num_skipped} skipped because the first message was sent after the specified time')
                elif num_skipped:
                    print(f'\rNo direct messages found matching the specified criteria ({num_skipped} checked)')
                else:
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

    def get_messages(self, sent_before: str = '', sent_after: str = '', keyword: str = '', before: int = 0, after: int = 0, limit: int = -1, timeout: int = 1, suppress_warning: bool = False, verbose: bool = False) -> List:
        """
        @brief Searches for messages meeting the given criteria
        @param sent_before      (str):  A date string formatted either as "MM/dd/yyyy or MM/dd/yyyy hh:mm:ss" indicating the
                                        time before which messages should have been sent
        @param sent_after       (str):  A date string formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss" indicating the
                                        time after which messages should have been sent
        @param keyword          (str):  A string of text which messages should contain
        @param before           (int):  The number of messages before each selected message to include in the returned set
        @param after            (int):  The number of messages after each selected message to include in the returned set
        @param limit            (int):  A limit of messages to fetch. -1 for no limit
        @param timeout          (int):  The number of seconds to wait before retrying an API call if a 429 error is received
        @param suppress_warning (bool): If no before or after dates are specified, the search is will need to traverse many
                                        groups and messages. A prompt is displayed by default requiring the user to confirm the
                                        search. Specifying this parameter as true bypasses this prompt, and immediately
                                        proceeds with the search
        @param verbose          (bool): Specifies if the search process should output periodic progress updates
        @return (List) A list of the message objects returned by the search
        """
        # Prompt if large search
        if sent_after == '' and not suppress_warning:
            choice = input('You have chosen to search for messages with no date range. Depending on how much you have used GroupMe, this search could take a long time. Do you want to continue (Y/N)? ')
            while choice.lower() != 'y' and choice.lower() != 'n':
                choice = input('Please select "Y" or "N" to indicate if you would like to continue with the search')
            if choice.lower() == 'y':
                if not verbose:
                    choice = input('Would you like to enable verbose mode so that progress of the search will be visible (Y/N)? ')
                    while choice.lower() != 'y' and choice.lower() != 'n':
                        choice = input('Please select "Y" or "N" to indicate if you would like to enable verbose mode')
                    if choice.lower() == 'y':
                        verbose = True
            else:
                print('Search canceled')
                return []

        start = time.time()

        chats = self.get_chats(used_after=sent_after, created_before=sent_before, timeout=timeout, verbose=verbose)

        messages = []
        for chat in chats:
            messages = messages + chat.get_messages(sent_before=sent_before, sent_after=sent_after, keyword=keyword, before=before, after=after, timeout=timeout, verbose=verbose)

        # Clean up result set
        messages.sort(key=lambda chat_message: chat_message.time_epoch)

        if before or after:
            if verbose:
                print('Pruning result set to remove duplicate messages...', end='')
            message_ids = []
            messages_to_remove = []
            for i, message in enumerate(messages):
                if message.id in message_ids:
                    messages_to_remove.append(message)
                else:
                    message_ids.append(message.id)
                if verbose:
                    print(f'\rPruning result set to remove duplicate messages {progress_bar(i, len(messages))}', end='')

            for message in messages_to_remove:
                messages.remove(message)
            if verbose:
                print('\rSuccessfully removed any duplicates from the result set')

        if limit != -1 and len(messages) > limit:
            messages = messages[0:limit]

        end = time.time()
        if verbose:
            seconds = end - start
            hours = math.floor(seconds/3600)
            seconds = seconds - (hours * 3600)
            minutes = math.floor(seconds/60)
            seconds = seconds - (minutes * 60)
            print('Total time: ', end='')
            if hours:
                print(f'{hours} hr ', end='')
            if hours or minutes:
                print(f'{minutes} min ', end='')
            print(f'{round(seconds)} sec')

        return messages


def get_cutoff(last_used: str, add_time: str = '00:00:00') -> int | None:
    """
    @brief  Takes either a date or a duration, and returns a timestamp referring to the date or that duration back from the current time
    @param  last_used (str): A string formatted either as "MM/dd/yyyy", "MM/dd/yyyy hh:mm:ss", or as a number followed by a single letter unit
    @param  add_time  (str): A string representing a time, formatted as hh:mm:ss, which is appended to the end of a date provided without a time
    @return (int) An integer representing a point in time
    """
    if last_used == '':
        return None

    date_components = last_used.split('/')
    if len(date_components) == 1:
        # If specified as duration get last three characters if minutes, or last character otherwise
        if last_used.endswith('min'):
            number = last_used[0:len(last_used) - 3]
            unit = last_used[len(last_used) - 3:]
        else:
            number = last_used[0:len(last_used) - 1]
            unit = last_used[len(last_used) - 1]

        # Verify that numeric portion is numeric
        try:
            number = int(number)
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = to_seconds(number, unit)
    elif len(date_components) == 3:
        # If specified as date, chop off time component and then split into date components
        date_components[2] = date_components[2].split(' ')[0]
        time_components = date_components[2].split(' ')[1:]
        if len(time_components) == 0:
            time_components = add_time.split(':')
        try:
            month = int(date_components[0])
            day = int(date_components[1])
            year = int(date_components[2])
            hour = int(time_components[0])
            minute = int(time_components[1])
            second = int(time_components[2])
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = time.time() - float(datetime(year, month, day, hour, minute, second).timestamp())
    else:
        raise GroupMeException('Invalid argument for argument "last_used"')
    return int(time.time() - timespan)
