"""
@package groupme
@brief   Classes to represent different kinds of GroupMe chats

@date    6/1/2024
@updated 7/20/2024

@author Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from typing import Dict

from common_utils import call_api
from time_functions import epoch_to_string


class Chat:
    """
    @brief Interface representing a GroupMe chat
    """
    def __init__(self):
        """
        @brief Constructor. Defaults all fields to None, since generic Chat objects are not created
        """
        self.name = None
        self.description = None
        self.last_used_epoch = None
        self.last_used = None
        self.creation_date_epoch = None
        self.creation_date = None


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
        self.name = data['name']
        self.description = data['description']
        self.last_used_epoch = data['messages']['last_message_created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
        self.owner = 'Unknown'
        group_data = call_api(f'groups/{data["id"]}', token)
        members = []
        for user in group_data['members']:
            if 'owner' in user['roles']:
                self.owner = user['name']
            members.append(user['name'])
        self.members = members


class DirectMessage(Chat):
    """
    @brief Represents a GroupMe direct message thread
    """
    def __init__(self, data: Dict):
        """
        @brief Constructor
        @param data (Dict): Dictionary of data representing the direct message chat as returned from a query
        """
        super().__init__()
        self.name = data['other_user']['name']
        self.last_used_epoch = data['last_message']['created_at']
        self.last_used = epoch_to_string(self.last_used_epoch)
        self.creation_date_epoch = data['created_at']
        self.creation_date = epoch_to_string(self.creation_date_epoch)
