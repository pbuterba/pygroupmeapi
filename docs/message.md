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
+ `emoji_mappings` - A dictionary mapping the emoji placeholder character for the message, to the charmap entries for the emojis. See the [GroupMe Docs](https://dev.groupme.com/docs/v3)
and the [GroupMe emoji docs](https://github.com/groupme-js/GroupMeCommunityDocs/blob/master/emoji.md) for more info