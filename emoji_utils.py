"""
@package    groupme
@brief      A script for handling GroupMe's "powerup" emojis

@date       2/19/2025
@updated    2/19/2025

@author     Preston Buterbaugh
@credit     https://github.com/groupme-js/GroupMeCommunityDocs/blob/master/emoji.md
@credit     https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
"""
# Imports
import io
import json
import os
from typing import List
from zipfile import ZipFile

import requests

from groupme.common_utils import GroupMeException


POWERUP_API = 'https://powerup.groupme.com/powerups'


def get_emoji_mappings(charmap: List, resolution: int = 2) -> List | None:
    """
    @brief  Downloads emojis used in a message, stores in current directory, and returns links
    @param  charmap (List):   The charmap as returned from a GroupMe request
    @param  resolution (int): An integer specifying the resolution of the emoji image according to the following scale:
        - 1: 160dpi
        - 2: 240dpi (default)
        - 3: 320dpi
        - 4: 480dpi
        - 5: 640dpi
    @return
        - (List) A list containing the links for each emoji referenced in the charmap
        - (None) If an invalid emoji pack or index was specified
    """
    for emoji in charmap:
        # Unpack charmap entry
        pack_id = emoji[0]
        emoji_index = emoji[1]

        # Request emoji data
        response = requests.get(POWERUP_API)
        if response.status_code != 200:
            raise GroupMeException(f'Could not fetch powerup emoji data. Request returned {response.status_code}')
        emoji_packs = json.loads(response.text)['powerups']

        # Get emoji pack
        emoji_pack = None
        for pack in emoji_packs:
            if pack['meta']['pack_id'] == pack_id:
                emoji_pack = pack
                break
        if emoji_pack is None:
            return None

        # Download emoji images
        transliteration = emoji_pack['meta']['transliterations'][emoji_index]
        zip_url = emoji_pack['meta']['inline'][resolution - 1]['zip_url']
        response = requests.get(zip_url)
        if not response.ok:
            raise GroupMeException('Failed to retrieve emoji images')
        zip_file = ZipFile(io.BytesIO(response.content))
        zip_file.extractall(os.getcwd())