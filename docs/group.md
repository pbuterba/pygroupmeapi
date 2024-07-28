# Group
The Group object represents a GroupMe group. It can be used to obtain information about the group itself or messages within the group

## Fields
The following fields are available to access on objects of the Group class
+ `id` - A string containing the the group's ID
+ `name` - A string containing the name of the group
+ `description` - A string containing the group's description
+ `last_used_epoch` - An integer containing the point in time at which the group was last used, stored as an epoch timestamp
+ `last_used` - A string containing the point in time at which the group was last used, formatted as "MM/dd/yyyy hh:mm:ss a"
+ `creation_date_epoch` - An integer containing the point in time at which the group was created, stored as an epoch timestamp
+ `creation_date` - A string containing the point in time at which the group was was created, formatted as "MM/dd/yyyy hh:mm:ss a"
+ `image_url` - A string containing the URL for the group's avatar picture

## Methods
The following methods may be called on objects of the Group class
```
owner()
```
Returns a string containing the name of the group's owner


```
members()
```
Returns a list of strings containing the names of each member of the group

```
get_messages(sent_before, sent_after, keyword, before, after, limit, verbose)
```
Returns a list of `Message` objects representing a subset of all messages sent in the group.

**Parameters:**
+ `sent_before` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 23:59:59 is assumed. If this
parameter is specified, only messages sent AT or BEFORE the specified time will be returned.
+ `sent_after` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 00:00:00 is assumed. If this
parameter is specified, only messages sent sent AT or AFTER the specified time will be returned.
+ `keyword` - *Optional*. A string of text. If specified, only messages containing this string of text will be returned.
+ `before` - *Optional*. An integer representing the number of messages appearing in the group chonologically immediately BEFORE each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately proceeding a message
containing the keyword text.
+ `after` - *Optional*. An integer representing the number of messages appearing in the group chonologically immediately AFTER each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately following a message
containing the keyword text.
+ `limit` - *Optional*.  An integer representing the maximum number of messages to be fetched from the group. Defaults to -1 which is interpreted as no limit. If more messages would
be returned, only the most recent ones are returned.
+ `verbose` - *Optional*. Boolean flag that defaults to false. If set to true, console output will update the user on the progress of the search. Useful for searches for large numbers
of messages. Since these will take a long time to complete, verbose output will assure the user that the process is still moving.