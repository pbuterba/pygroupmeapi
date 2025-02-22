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
All the functionality of the API should be accessible through the base [`GroupMe`](docs/base_object.md) object, which can be imported to a file with the following line of code:
```
from groupme import GroupMe
```
The `GroupMe` object will return values of other object types that are defined in this project, so you may wish to import thsese as well if using Python type hinting. Other classes
available are [`Group`](docs/group.md), [`DirectMessage`](docs/direct_message.md), `Chat` (a superclass that includes both `Group` and `DirectMessage`), and [`Message`](docs/message.md).
See the [individual APIs](docs) for each object to see more information on their attributes and methods.

## Changelog
+ v2.0.0 - February 21st, 2025
  + Made timeout for API call throttling configurable
  + Changed Message `emoji_mappings` field to contain just the charmap as a nested list, instead of a dictionary with the emoji replacement character as a key
  + Added `emoji_replacement_char` field to `Message` class, containing the character that is substituted in for powerup emojis
  + Added methods to download and subsequently delete local image files for powerup emojis used in a `Message` instance
  + Added method to obtain information about messages that are replied to by other messages
+ v1.0.3 - December 20th, 2024
  + Added check for API call throttling
+ v1.0.2 - September 5th, 2024
  + Fixed bug where Chat abstract class did not recognize "before" and "after" parameters in get_messages() function
  + Fixed bug which only allowed group searches to fetch messages 20 at a time (GroupMe hardcoded limit for direct messages), rather than 100 at a time (GroupMe hardcoded limit for groups)
+ v1.0.1 - July 28th, 2024
  + Fixed module import error that prevented the package from being used
+ v1.0.0 - July 27th, 2024
  + Initial release