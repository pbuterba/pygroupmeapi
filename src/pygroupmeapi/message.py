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
@package    pygroupmeapi
@brief      Class representing a GroupMe message object

@date       7/23/2024
@updated    5/14/2025

@author     Preston Buterbaugh
@credit     GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from __future__ import annotations
import os
from typing import Dict

from .requester import Requester
from .emoji_utils import get_emoji_links
from .time_functions import epoch_to_string


class Message:
    """
    @brief Class representing a GroupMe message
    """

    def __init__(self, name: str, is_group: bool, data: Dict, requester: Requester):
        """
        @brief Message constructor
        @param name      (str):       The name of the chat in which the message was sent
        @param is_group  (bool):      If the message was sent in a group (as opposed to a direct message)
        @param data      (Dict):      The dictionary of data representing the message, as returned by the API
        @param requester (Requester): The requester object for the session (instantiated at the user level)
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
        self.emoji_replacement_char = None
        self.emoji_urls = None
        self.reply_message_id = None
        self._requester = requester
        if 'attachments' in data.keys():
            for attachment in data['attachments']:
                if attachment['type'] == 'image':
                    self.image_urls.append(attachment['url'])
                elif attachment['type'] == 'emoji':
                    self.emoji_mappings = attachment['charmap']
                    self.emoji_replacement_char = attachment['placeholder']
                elif attachment['type'] == 'reply':
                    self.reply_message_id = attachment['reply_id']

    def replied_message(self) -> Message | None:
        """
        @brief  Returns the message that the current message is a reply to, or None if it is not a reply
        @return
            - (Message) The message being replied to
            - (None)    If the message is not a reply, or the message to which it is a reply could not be found
        """
        if self.reply_message_id is not None:
            # Get chat in which message was sent
            _, chat_data = self._requester.request_chat(self.chat, self.is_group)
            if chat_data is None:
                return None
            if self.is_group:
                chat_id = chat_data['id']
            else:
                chat_id = chat_data['other_user']['id']

            chat_type = 'G' if self.is_group else 'D'
            message_cache_id = f'{chat_type}_{chat_id}_{self.reply_message_id}'
            message_data = self._requester.request_message(message_cache_id)
            if message_data is None:
                replied_message = None
            else:
                replied_message = Message(self.chat, self.is_group, message_data, self._requester)
            return replied_message
        return None

    def download_emojis(self, resolution: int = 2):
        """
        @brief  Downloads image files of all of GroupMe's "powerup" emojis that are used in the message, and populates
        the object's "emoji_urls" field with a list of URLs to these images
        @param  resolution (int): An integer specifying the resolution of the emoji image according to the following scale:
            - 1: 160dpi
            - 2: 240dpi (default)
            - 3: 320dpi
            - 4: 480dpi
            - 5: 640dpi
        """
        self.emoji_urls = get_emoji_links(self.emoji_mappings, resolution)

    def delete_local_emojis(self):
        """
        @brief  Deletes any image files downloaded with the download_emojis() function
        """
        if self.emoji_urls is not None:
            for url in self.emoji_urls:
                os.remove(url)
            self.emoji_urls = None
