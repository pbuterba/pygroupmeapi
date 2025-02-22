# Direct Message
The Direct Message object represents a GroupMe direct message chat. It can be used to obtain information about the chat itself or messages sent in the direct message

## Fields
The following fields are available to access on objects of the DirectMessage class
+ `id` - A string containing the user ID of the other user in the direct message
+ `name` - A string containing the user name of the other user in the direct message
+ `last_used_epoch` - An integer containing the point in time at which the last message was sent, stored as an epoch timestamp
+ `last_used` - A string containing the point in time at which the the last message was sent, formatted as "MM/dd/yyyy hh:mm:ss a"
+ `creation_date_epoch` - An integer containing the point in time at which the first message was sent, stored as an epoch timestamp
+ `creation_date` - A string containing the point in time at which the first message was sent, formatted as "MM/dd/yyyy hh:mm:ss a"
+ `image_url` - A string containing the URL of the profile picture of the other user in the direct message

## Methods
The following methods may be called on objects of the Direct Message class
```
get_messages(sent_before, sent_after, keyword, before, after, limit, timeout, verbose)
```
Returns a list of `Message` objects representing a subset of all messages sent in the group.

**Parameters:**
+ `sent_before` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 23:59:59 is assumed. If this
parameter is specified, only messages sent AT or BEFORE the specified time will be returned.
+ `sent_after` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 00:00:00 is assumed. If this
parameter is specified, only messages sent sent AT or AFTER the specified time will be returned.
+ `keyword` - *Optional*. A string of text. If specified, only messages containing this string of text will be returned.
+ `before` - *Optional*. An integer representing the number of messages appearing in the chat chonologically immediately BEFORE each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately proceeding a message
containing the keyword text.
+ `after` - *Optional*. An integer representing the number of messages appearing in the chat chonologically immediately AFTER each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately following a message
containing the keyword text.
+ `limit` - *Optional*.  An integer representing the maximum number of messages to be fetched from the chat. Defaults to -1 which is interpreted as no limit. If more messages would
be returned, only the most recent ones are returned.
+ `timeout` - *Optional*. The number of seconds that should be waited before re-attempting an API call if a call is denied due to receiving too many API calls in a given period of
time. Defaults to 1 second.
+ `verbose` - *Optional*. Boolean flag that defaults to false. If set to true, console output will update the user on the progress of the search. Useful for searches for large numbers
of messages. Since these will take a long time to complete, verbose output will assure the user that the process is still moving.