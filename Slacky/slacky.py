import os

import slack

from slacky_block_builder import SlackyBlockBuilder
import slacky_config as cfg


class Slacky:

    def __init__(self):
        # Slacky internal setup
        self.bb = SlackyBlockBuilder()

        # Setup connection with Slack Workspace
        self.token = os.environ['SLACK_API_TOKEN']
        self.client = slack.WebClient(token=self.token)

        # Get channels in workspace
        self.channels = self.get_channels()

    def parse(self, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        messages = self.get_messages(channel_id=channel_id)
        if not messages:
            return
        # self.delete_nuclear(channel_id=channel_id, confirmation_override=True)
        self.send_messages(self.bb.parse(messages), channel_id=channel_id)

    def get_channels(self):
        """Returns a list of channels in the workspace
        Required Slack API Scopes:
            channels:read
            groups:read
        """
        response = self.client.api_call(
            f'conversations.list?types={cfg.CHANNEL["types"]}&exclude_archived={cfg.CHANNEL["exclude_archived"]}',
        )
        assert response['ok']
        return response['channels']

    def find_channel_id(self, channel_name):
        """Returns the channel id of the given channel name"""
        for channel in self.channels:
            if channel_name == channel['name']:
                return channel['id']
        raise NameError(f"{self.find_channel_id.__name__}: Channel with given name not found")

    def get_messages(self, channel_name=None, channel_id=None):
        """Returns a list of messages in the given channel
        Required Slack API Scopes:
            channels:history
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        response = self.client.api_call(
            f'channels.history?channel={channel_id}'
        )
        assert response['ok']
        return response['messages']

    def send_messages(self, blocks, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        print(blocks)
        self.client.api_call(
            f'chat.postMessage?'
            f'as_user={cfg.POST["as_user"]}&'
            f'channel={channel_id}&'
            f'blocks={blocks}'
        )

    def delete_slack_generated(self, channel_name=None, channel_id=None):
        self.delete_nuclear(
            channel_name=channel_name, channel_id=channel_id, confirmation_override=True,
            restrict={'type': 'subtype', 'values': cfg.SUBTYPES}
        )

    def delete_bot_messages(self, channel_name=None, channel_id=None):
        self.delete_nuclear(
            channel_name=channel_name, channel_id=channel_id, confirmation_override=True,
            restrict={'type': 'subtype', 'values': ['bot_message']}
        )

    def delete_nuclear(self, channel_name=None, channel_id=None, confirmation_override=False, restrict=None):
        """Deletes every message in a given channel
        Required Slack API Scopes:
            chat:write:user
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        if not confirmation_override:
            confirmation = input(
                f"Are you sure you want to delete all messages from the channel #{channel_name}? Y/N\n")
            if 'Y' not in confirmation:
                print(f"Aborting nuclear delete on channel #{channel_name}")
                return
        for message in self.get_messages(channel_id=channel_id):
            if not restrict or (restrict['type'] in message and message[restrict['type']] in restrict['values']):
                response = self.client.api_call(
                    f'chat.delete?channel={channel_id}&ts={message["ts"]}'
                )
                assert response['ok']
