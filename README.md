# Slack Toolkit

## Introduction

A collection of tools for managing Slack through the versatility and comfort of python.

## Slacky

Slacky is a simple pythonic wrapper for the Slack API calls, which allow the programmer to quickly set up a project with any functionalities that may be required. 

To use Slacky, an app must be created in the Slack developer section and the token must be supplied in one's environment variables.

Depending on the token type used, some functionalities may be limited or unavailable. For development purposes, the user token (default) is used.

For the appropriate methods to work, the app must be given the appropriate Slack API Scopes. It is advised to only apply the ones which are required. These are conveniently listed in the docstrings of the respective Slacky method.

### Slacky methods

Currently Slacky may be utilized to:

* Get a list of the channels in a workspace
* Retrieve the messages in a given channel
* Send a message (or reply) to a given channel
* Update a message
* Upload a file as a message or reply
* Manipulate the files of a Slack workspace
	* Remove all files not appearing in any channel, group or ims
	* Adjust scope of file (public/private)
* Extensively remove messages in a channel
	* All messages
	* Selected messages
	* Bot messages
	* Slack messages
	* Etc.

## Emoji Control

Emoji Control is a simple bot which allows adding emoji to a Slack workspace programmatically. 

The bot accepts a Slack client object (which can be the Slacky client if used in conjunction) and may accept a token. Please read below on token types when dealing with emoji.

Currently three methods to add emoji are implemented:

* From link - The url should point to an image or gif.
* From file - Filepath should point to an image or gif.
* Favicon - Will turn the favicon of a page into an emoji for your Slack workspace.

Due to limitations in the Slack API, the token supplied must be a user token. To find your user token, open any window in your respective Slack workspace and enter the following command into the browser console `window.prompt("your api token is: ", window.boot_data.api_token)`. If emoji manipulation is turned off for normal users, you must be an administrator of the workspace.

## Tools in progress/Roadmap

### Formatting

A tool for easy formatting of storage/informational channels will soon be available.

### Future plans

Slacky shall be made available through pip.
