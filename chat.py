"""
@package groupme
@brief   Classes to represent different kinds of GroupMe chats

@date    6/1/2024
@updated 7/23/2024

@author Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
import math
from typing import List, Dict

from common_utils import call_api
from message import Message
from time_functions import string_to_epoch, epoch_to_string


class Chat:
    """
    @brief Interface representing a GroupMe chat
    """
    def __init__(self):
        """
        @brief Constructor. Defaults all fields to None, since generic Chat objects are not created
        """
        self.id = None
        self.name = None
        self.description = None
        self.last_used_epoch = None
        self.last_used = None
        self.creation_date_epoch = None
        self.creation_date = None
        self.token = None

    def get_messages(self, before: str = '', after: str = '', keyword: str = '', limit: int = -1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a chat matching the specified criteria
        @param  before  (int): The time prior to which all messages returned should have been sent
        @param  after   (int): The time at or after which all messages returned should have been sent
        @param  keyword (str): A string of text which all messages returned should contain
        @param  limit   (int): The maximum number of messages to return. -1 returns all matching messages
        @param  verbose (bool): If output should be displayed indicating progress made in the query
        @return (List) A list of Message objects
        """
        raise NotImplementedError('Cannot call abstract method')


class Group(Chat):
    """
    @brief Represents a GroupMe group
    """
    def __init__(self, data: Dict, token: str):
        """
        @brief Constructor
        @param data (Dict): Dictionary of data representing the group as returned from a query
        @param token (str): The token for fetching group data
        """
        super().__init__()
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.last_used_epoch = data['messages']['last_message_created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
        self.token = token

    def owner(self) -> str:
        group_data = call_api(f'groups/{self.id}', self.token)
        for user in group_data['members']:
            if 'owner' in user['roles']:
                return user['name']
        return 'Unknown'

    def members(self) -> List:
        group_data = call_api(f'groups/{self.id}', self.token)
        return [user['nickname'] for user in group_data]

    def get_messages(self, before: str = '', after: str = '', keyword: str = '', limit: int = -1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a group matching the specified criteria (see superclass method parameter documentation)
        """
        return page_through_messages(self.id, self.token, self.name, True, before, after, keyword, limit, verbose)


class DirectMessage(Chat):
    """
    @brief Represents a GroupMe direct message thread
    """
    def __init__(self, data: Dict, token: str):
        """
        @brief Constructor
        @param data  (Dict): Dictionary of data representing the direct message chat as returned from a query
        @param token (str):  GroupMe authentication token
        """
        super().__init__()
        self.id = data['other_user']['id']
        self.name = data['other_user']['name']
        self.last_used_epoch = data['last_message']['created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
        self.token = token

    def get_messages(self, before: str = '', after: str = '', keyword: str = '', limit: int = -1, verbose: bool = False) -> List:
        """
        @brief  Gets all messages in a direct message matching the specified criteria (see superclass method parameter documentation)
        """
        return page_through_messages(self.id, self.token, self.name, False, before, after, keyword, limit, verbose)


def page_through_messages(chat_id: str, token: str, name: str, is_group: bool, before: str, after: str, keyword: str, limit: int, verbose: bool) -> List:
    """
    @brief  Pages through messages in a chat and returns the messages matching the specified criteria
    @param  chat_id             (str):  The ID of the chat from which to retrieve the message data
    @param  token               (str):  GroupMe authentication token
    @param  name                (str):  The chat name
    @param  is_group            (bool): If the chat is a group (as opposed to a direct message)
    @param  before              (str):  The time or date at or before which all returned messages should have been sent
    @param  after               (str):  The time or date at or after which all returned messages should have been sent
    @param  keyword             (str):  A string of text which all returned messages should contain
    @param  limit               (int):  The maximum number of messages to return from this group. -1 for no limit
    @param  verbose             (bool): If output detailing the progress of the search should be shown
    @return (List) A list of all messages in the group matching the criteria
    """
    if verbose:
        print(f'Fetching messages from {name}...', end='')

    # Calculate before and after times
    if before:
        if len(before.split(' ')) == 1:
            before = f'{before} 23:59:59'
        before = string_to_epoch(before)

    if after:
        if len(after.split(' ')) == 1:
            after = f'{after} 00:00:00'
        after = string_to_epoch(after)

    # Variables for tracking progress
    messages = []
    num_skipped = 0
    in_range = True

    # Determine endpoint
    if is_group:
        endpoint = f'groups/{chat_id}/messages'
    else:
        endpoint = 'direct_messages'

    # Set parameters
    params = {}
    if is_group:
        # Calculate effective limit
        if limit == -1:
            effective_limit = 100
        else:
            effective_limit = min(limit - len(messages), 100)
        params['limit'] = effective_limit
    else:
        params['other_user_id'] = chat_id

    message_page = call_api(endpoint, token, params=params, except_message=f'Error fetching messages from {name}')
    total_messages = message_page['count']
    if is_group:
        message_page = message_page['messages']
    else:
        message_page = message_page['direct_messages']
    while len(message_page) > 0 and in_range:
        for i, message in enumerate(message_page):
            if after and message['created_at'] < after:
                in_range = False
                break
            if (before and message['created_at'] > before) or (keyword and (message['text'] is None or keyword not in message['text'])):
                num_skipped = num_skipped + 1
            else:
                messages.append(Message(name, is_group, message))
            if verbose:
                print(f'\rFetching messages from {name} (searched {len(messages) + num_skipped} of {total_messages}, selected {len(messages)})', end='')
                if after:
                    print('...', end='')
                else:
                    # Since the search will proceed all the way to the beginning of the group, output progress bar
                    progress = (len(messages) + num_skipped)/total_messages
                    ticks = math.floor((progress * 100)/2)
                    print(' ', end='')
                    for _ in range(ticks):
                        print('=', end='')
                    for _ in range(50 - ticks):
                        print('-', end='')
                    print(f' {round(progress * 100)}%', end='')

            # Update last message ID if last message on page
            if i == len(message_page) - 1:
                params['before_id'] = message['id']

        # Calculate new effective limit
        if is_group:
            if limit == -1:
                effective_limit = 100
            else:
                effective_limit = min(limit - len(messages), 100)
            params['limit'] = effective_limit

        message_page = call_api(endpoint, token, params=params, except_message=f'Error fetching messages from {name}')
        if is_group:
            message_page = message_page['messages']
        else:
            message_page = message_page['direct_messages']

    if verbose:
        print(f'\rSelected {len(messages)} of {total_messages} messages from {name}')
    return messages
