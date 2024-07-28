# GroupMe API
This Python API allows you to interact with GroupMe

## Setup
To make use of this tool, it is necessary to first set up an API token on the [GroupMe Developer page](dev.groupme.com)

### Logging into the developer page
Log in to the page using the "Log In" button in the top right corner, and entering your email
and password for your GroupMe account.

### A note if you use a third-party app to sign in to GroupMe
If you use Facebook, Apple, Microsoft, or another login service to access your
GroupMe account, you may need to first set up a password for your account. The only way I know to do this is using
GroupMe's "Forgot password" feature. Visit the [forgot password](https://web.groupme.com/forgot_password) page, and
enter the email address associated with your account (you can find this by clicking on your profile picture in the
bottom right corner of GroupMe in the web browser, and selecting "Profile" from the resulting menu).

### Getting your API token
Once you have entered your email and password on the developer page, you may also be prompted to enter a code sent to your
SMS or email to verify your identity. Once you are successfully logged in, select "Access Token" in the top right (next to
your account name), and you will be presented with a pop-up containing a long string of characters. Copy these, and save
them somewhere secure. This is your token which grants you access to the GroupMe API. Tokens allow you to sign in to a web service,
fulfilling the role of a combined username and password. As such, they should be treated with the same security level as passwords.

## Usage
All the functionality of the API should be accessible through the base `GroupMe` object, which can be imported to a file with the following line of code:
```
from groupme import GroupMe
```
The GroupMe object will return values of other object types that are defined in this project, so you may wish to import thsese as well if using Python type hinting. Other classes
available are [`Group`](docs/group.md), [`DirectMessage`](docs/direct_message.md), `Chat` (a superclass that includes both `Group` and `DirectMessage`), and [`Message`](docs/message.md). See the [individual APIs](docs)
for each of these objects for more information on their attributes and methods.

### The GroupMe Object
The GroupMe object contains top-level information about the user's GroupMe account. As such, it may also be thought of as representing a GroupMe user. From it, one can get information
on the user's chats and messages.

#### Constructor
```
user = GroupMe(token)
```
**Parameters:**
`token` is a string representing the GroupMe API token of the user whose account information will be fetched. See [Setup](#setup) for more information on this.

#### Fields
The following fields are available to access on objects of the GroupMe class
+ `name` - A string containing the user's name as listed on the GroupMe account
+ `email` - A string containing the email address associated with the GroupMe account
+ `phone_number` - A string containing the phone number linked to the user's GroupMe account

#### Methods
The following methods may be called on objects of the GroupMe class
```
get_chat(chat_name, is_dm)
```
Returns a `Chat` object representing a GroupMe chat to which the user has access.

**Parameters:**
+ `chat_name` - The name of the chat to be returned
+ `is_dm` - *Optional*. A performance enhancing flag, which defaults to false. If set to false, all groups will be searched to find a match to the provided chat name, before searching
any direct messages. If instead this flag is set to true, the search will traverse over the user's direct message channels, without checking any groups.

```
get_chats(used_after, created_before, verbose)
```
Returns a list of `Chat` objects representing all or a subset of all of the user's chats

**Parameters:**
+ `used_after` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 00:00:00 is assumed. If this
parameter is specified, only chats which have had at least one message sent AT or AFTER the specified time will be returned. Useful for filtering out old, dormant chats that have not
been used recently.
+ `created_before` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 23:59:59 is assumed. If this
parameter is specified, only chats which were created AT or BEFORE the specified time will be returned.
+ `verbose` - *Optional*. A boolean flag, defaults to false. If true, console output will update the user on how many chats have been retrieved from GroupMe so far. Useful for users
with large numbers of chats, since the search may take a long time, verbose output will assure the user that the process is still moving.

```
get_messages(sent_before, sent_after, keyword, before, after, limit, suppress_warning, verbose)
```
Returns a list of `Message` objects representing all or a subset of all GroupMe messages that the user has either sent or received. Running calling this function for a user who has
used GroupMe a lot could take a long time to complete. See parameter options for filtering.

**Parameters:**
+ `sent_before` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 23:59:59 is assumed. If this
parameter is specified, only messages sent AT or BEFORE the specified time will be returned.
+ `sent_after` - *Optional*. A string representing a date and time, formatted either as "MM/dd/yyyy" or "MM/dd/yyyy hh:mm:ss". If the former, a time of 00:00:00 is assumed. If this
parameter is specified, only messages sent sent AT or AFTER the specified time will be returned.
+ `keyword` - *Optional*. A string of text. If specified, only messages containing this string of text will be returned.
+ `before` - *Optional*. An integer representing the number of messages appearing in a chat chonologically immediately BEFORE each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately proceeding a message
containing the keyword text.
+ `after` - *Optional*. An integer representing the number of messages appearing in a chat chonologically immediately AFTER each message matching the search criteria, that should 
be returned, even if these messages do not match the search criteria. Most effective when paired with the `keyword` parameter, to fetch the context immediately following a message
containing the keyword text.
+ `limit` - *Optional*.  An integer representing the maximum number of messages to be returned by the function. Defaults to -1 which is interpreted as no limit. If more messages would
be returned, only the oldest ones are returned. *NOTE - Due to the structure of GroupMe's underlying API, messages much be fetched one group at a time. Because of this, all messages need to be fetched before limiting the number, so use of this parameter does not necessarily improve performance on otherwise long searches*
+ `suppress_warning` - *Optional*. Boolean flag that defaults to false. If the `sent_after` parameter is not specified, a warning is output by default stating that the search may take a long time,
as it will need to search back to the beginning of every chat. The user must type "y" or "n" to confirm continuing with the search. If the `verbose` flag is not set and the user chooses to continue,
another prompt will appear asking if the user would like to enable verbose mode, since the search is expected to be long. Setting this parameter to true prevents either of these warnings
from appearing, allowing the program to run without interruption.
+ `verbose` - *Optional*. Boolean flag that defaults to false. If set to true, console output will update the user on the progress of the search. Useful for searches for large numbers
of messages. Since these will take a long time to complete, verbose output will assure the user that the process is still moving.

## Changelog
+ v1.0.0 - July 27th, 2024
++ Initial release