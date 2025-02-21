# Message
The Message class represents an individual message sent in either a GroupMe group, or a direct message

## Fields
The following fields are available to access on objects of the Message class
+ `chat` - A string containing the name of the chat in which the message was sent (either the group name or the user name of the other user in a direct message)
+ `id` - A string containing the message's internal GroupMe message ID
+ `author` - A string containing the name of the user who sent the message
+ `author_profile_picture_url` - A string containing the URL of the message author's profile picture
+ `time_epoch` - An integer containing the point in time at which the message was sent, formatted as an epoch timestamp
+ `time` - A string containing the point in time at which the message was sent, formatted as "MM/dd/yyyy hh:mm:ss a"
+ `text` - A string containing the text of the message
+ `is_group` - A boolean flag indicating if the message was sent in a group versus a direct message
+ `img_urls` - A list of strings containing the URLs for all images included in the message
+ `emoji_mappings` - The charmap entries for any GroupMe powerup emojis used in the message. See the [GroupMe Docs](https://dev.groupme.com/docs/v3)
and the [GroupMe emoji docs](https://github.com/groupme-js/GroupMeCommunityDocs/blob/master/emoji.md) for more info. Defaults to `None` type if no powerup emojis
are used in the message
+ `reply_message_id` - A string containing the id of the message to which the given message is a reply to. If the message is not a reply, this field has the value `None`

## Methods
The following methods may be called on objects of the Message class:
```
get_emoji_links(resolution)
```
Downloads the image files corresponding to each powerup emoji used in the message, to the current working directory of the script, and returns a `List` containing the full URLs to
each of the downloaded local files.

**Parameters**:
+ `resolution` - *Optional*. An integer representing the resolution option to use when downloading the emoji image files:
  + 1: 160dpi
  + 2: 240dpi (default)
  + 3: 320dpi
  + 4: 480dpi
  + 5: 640dpi
```
replied_message()
```
Returns a `Message` object corresponding to the message to which the current message is a reply. Returns `None` if the current message is not a reply, or if the message being replied
to could not be found.