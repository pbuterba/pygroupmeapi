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
@package    groupme
@brief      A script for handling GroupMe's "powerup" emojis

@date       2/19/2025
@updated    2/20/2025

@author     Preston Buterbaugh
@credit     https://github.com/groupme-js/GroupMeCommunityDocs/blob/master/emoji.md
@credit     https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url
"""
# Imports
import json
import os
from typing import List
from zipfile import ZipFile

import requests

from groupme.common_utils import GroupMeException


POWERUP_API = 'https://powerup.groupme.com/powerups'


def get_emoji_links(charmap: List, resolution: int) -> List | None:
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
    # Request emoji data
    response = requests.get(POWERUP_API)
    if response.status_code != 200:
        raise GroupMeException(f'Could not fetch powerup emoji data. Request returned {response.status_code}')
    emoji_packs = json.loads(response.text)['powerups']

    # Lists to hold emoji data
    emoji_urls = []
    cached_charmap_entries = []
    downloaded_packs = []

    # Loop over all charmap entries
    for emoji in charmap:
        # Skip if already cached
        if emoji in cached_charmap_entries:
            continue

        # Unpack charmap entry
        pack_id = emoji[0]
        emoji_index = emoji[1]

        # Get emoji pack data
        emoji_pack = None
        for pack in emoji_packs:
            if pack['meta']['pack_id'] == pack_id:
                emoji_pack = pack
                break
        if emoji_pack is None:
            return None
        transliteration = emoji_pack['meta']['transliterations'][emoji_index]

        # Download emoji pack if not already downloaded
        if f'pack_{pack_id}.zip' not in downloaded_packs:
            zip_url = emoji_pack['meta']['inline'][resolution - 1]['zip_url']
            response = requests.get(zip_url, stream=True)
            if not response.ok:
                raise GroupMeException('Failed to retrieve emoji images')
            zip_file = open(f'pack_{pack_id}.zip', 'wb')
            for chunk in response.iter_content(chunk_size=128):
                zip_file.write(chunk)
            zip_file.close()
            downloaded_packs.append(f'pack_{pack_id}.zip')

        # Extract image
        zip_file = ZipFile(f'{os.getcwd()}\\pack_{pack_id}.zip')
        zip_file.extract(f'{emoji_index}.png', f'{os.getcwd()}')
        zip_file.close()
        os.rename(f'{emoji_index}.png', f'{transliteration}.png')

        emoji_urls.append(f'{os.getcwd()}\\{transliteration}.png')
        cached_charmap_entries.append(emoji)

    # Delete zip archives
    for pack in downloaded_packs:
        os.remove(pack)

    return emoji_urls
