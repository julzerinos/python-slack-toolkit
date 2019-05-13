import os
import slack


class SlackySettings:

    def __init__(self):
        # Settings for get_channels
        self.exclude_archived = 'true'
        self.types = 'public_channel,private_channel'


class Slacky:

    def __init__(self):
        # Slacky internal setup
        self.settings = SlackySettings()

        # Setup connection with Slack Workspace
        self.token = os.environ['SLACK_API_TOKEN']
        self.client = slack.WebClient(token=self.token)

        # Get channels in workspace
        self.channels = self.get_channels()



    def get_channels(self):
        """Returns a list of channels in the workspace
        Required Slack API Scopes:
            channels:read
            groups:read
        """
        response = self.client.api_call(
            f'conversations.list?types={self.settings.types}&exclude_archived={self.settings.exclude_archived}',
        )
        assert response['ok']
        return response['channels']

    def find_channel_id(self, channel_name):
        """Returns the channel id of the given channel name"""
        for channel in self.channels:
            if channel_name == channel['name']:
                return channel['id']
        raise NameError(f"{self.find_channel_id.__name__}: Channel with given name not found")

    def get_messages(self, channel):
        """Returns a list of messages in the given channel
        Required Slack API Scopes:
            channels:history
        """
        response = self.client.api_call(
            f'channels.history?channel={channel}'
        )
        assert response['ok']
        return response['messages']

    def format_messages(self):
        pass

    def nuclear_delete(self, channel):
        """Deletes every message in a given channel
        Required Slack API Scopes:
            chat:write:user
        """
        channel_id = self.find_channel_id(channel)
        confirmation = input(f"Are you sure you want to delete all messages from the channel {channel}? Y/N\n")
        if 'Y' not in confirmation:
            print(f"Aborting nuclear delete on channel {channel}")
            return
        for message in self.get_messages(channel_id):
            response = self.client.api_call(
                f'chat.delete?channel={channel_id}&ts={message["ts"]}'
            )
            assert response['ok']


if __name__ == '__main__':
    slacky = Slacky()
    slacky.format_messages()