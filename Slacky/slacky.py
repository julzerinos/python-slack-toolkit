import os
import re
import slack


class SlackyBlockBuilder:

    DIVIDER_BLOCK = {
        "type": "divider"
    }

    def parse(self, messages):
        self.message_type_switch(messages)
        return self.format_messages(messages)

    def message_type_switch(self, messages):
        for message in messages:
            print(message)
            if 'bot_id' in message:
                print('bot-generated')
            elif 'files' in message:
                print('has files')
            else:
                print('is other')

    def link_text_constructor(self, text):
        pass

    def format_messages(self, messages):
        new_messages = []
        for i, message in enumerate(messages):
            new_messages.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': self.format_linktext(i, message)
                }
            })
        return new_messages

    def format_linktext(self, i, message):
        links = re.findall('<([^<>]*)>', message['text'])
        if not links:
            return 'E[tried to create text with link without link]'
        text = re.sub(r'(<.*>)', '', message['text'])
        return f"*{str(i).zfill(3)}*\t_{text}_ {' '.join([f'<{link}|link>' for link in links])}"


class SlackySettings:

    def __init__(self):
        # Settings for get_channels
        self.exclude_archived = 'true'
        self.types = 'public_channel,private_channel'


class Slacky:

    def __init__(self):
        # Slacky internal setup
        self.settings = SlackySettings()
        self.block_builder = SlackyBlockBuilder()

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

    def parse(self, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        messages = self.get_messages(channel_id=channel_id)
        if not messages:
            return
        self.client.api_call(
            f'chat.postMessage?as_user=false&channel={channel_id}&blocks={self.block_builder.parse(messages)}'
        )

    def nuclear_delete(self, channel_name=None, channel_id=None):
        """Deletes every message in a given channel
        Required Slack API Scopes:
            chat:write:user
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        confirmation = input(f"Are you sure you want to delete all messages from the channel #{channel_name}? Y/N\n")
        if 'Y' not in confirmation:
            print(f"Aborting nuclear delete on channel #{channel_name}")
            return
        for message in self.get_messages(channel_id=channel_id):
            response = self.client.api_call(
                f'chat.delete?channel={channel_id}&ts={message["ts"]}'
            )
            assert response['ok']


if __name__ == '__main__':
    slacky = Slacky()
    # slacky.nuclear_delete('testing')
    slacky.parse('testing')
