"""
@package    groupme
@brief      Class representing a GroupMe message object

@date       7/23/2024
@updated    2/21/2025

@author     Preston Buterbaugh
@credit     GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from __future__ import annotations
import os
from typing import List, Dict

from groupme.common_utils import call_api
from groupme.emoji_utils import get_emoji_links
from groupme.time_functions import epoch_to_string


class Message:
    """
    @brief Class representing a GroupMe message
    """

    def __init__(self, name: str, is_group: bool, data: Dict, token: str):
        """
        @brief Message constructor
        @param name     (str):  The name of the chat in which the message was sent
        @param is_group (bool): If the message was sent in a group (as opposed to a direct message)
        @param data     (Dict): The dictionary of data representing the message, as returned by the API
        @param token    (str):  The user's GroupMe token used for fetching further data from the API
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
        self.token = token
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
            - (None)    If the message is not a reply
        """
        if self.reply_message_id is not None:
            # Get chat in which message was sent
            chat_id = None
            if self.is_group:
                groups = call_api('groups', self.token)
                for group in groups:
                    if group['name'] == self.chat:
                        chat_id = group['id']
                        break
            else:
                dms = call_api('chats', self.token)
                for dm in dms:
                    if dm['other_user']['name'] == self.chat:
                        chat_id = dm['other_user']['id']
                        break

            # Get first page of messages
            chat_name = self.chat
            last_id = self.id
            if self.is_group:
                params = {
                    'before_id': last_id,
                    'limit': 100
                }
                message_page = call_api(f'groups/{chat_id}/messages', self.token, params=params, except_message='Error fetching reply information')['messages']
            else:
                params = {
                    'other_user': chat_id,
                    'before_id': last_id
                }
                message_page = call_api('direct_messages', self.token, params=params, except_message='Error fetching reply information')['direct_messages']

            # Loop until reply is found
            while len(message_page) > 0:
                for message in message_page:
                    if message['id'] == self.reply_message_id:
                        return Message(chat_name, self.is_group, message, self.token)
                    last_id = message['id']

                if self.is_group:
                    params = {
                        'before_id': last_id,
                        'limit': 100
                    }
                    message_page = call_api(f'groups/{chat_id}/messages', self.token, params=params, except_message='Error fetching reply information')['messages']
                else:
                    params = {
                        'other_user': chat_id,
                        'before_id': last_id
                    }
                    message_page = call_api(f'direct_messages', self.token, params=params, except_message='Error fetching reply information')['direct_messages']

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
