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



## Tools in progress/Roadmap



### Formatting



A tool for easy formatting of storage/informational channels will soon be available.



### Future plans



Slacky shall be made available through pip.
