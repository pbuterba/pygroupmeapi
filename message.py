"""
@package    groupme
@brief      Class representing a GroupMe message object

@date       7/23/2024
@updated    7/27/2024

@author     Preston Buterbaugh
@credit     GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from typing import Dict

from time_functions import epoch_to_string


class Message:
    """
    @brief Class representing a GroupMe message
    """

    def __init__(self, name: str, is_group: bool, data: Dict):
        """
        @brief Message constructor
        @param name     (str):  The name of the chat in which the message was sent
        @param is_group (bool): If the message was sent in a group (as opposed to a direct message)
        @param data     (Dict): The dictionary of data representing the message, as returned by the API
        """
        self.chat = name
        self.id = data['id']
        self.author = data['name']
        self.author_profile_picture_url = data['avatar_url']
        self.time_epoch = data['created_at']
        self.time = epoch_to_string(self.time_epoch)
        self.text = data['text']
        self.is_group = is_group
        self.image_urls = []
        self.emoji_mappings = None
        if 'attachments' in data.keys():
            for attachment in data['attachments']:
                if attachment['type'] == 'image':
                    self.image_urls.append(attachment['url'])
                elif attachment['type'] == 'emoji':
                    self.emoji_mappings = {attachment['placeholder']: attachment['charmap']}
