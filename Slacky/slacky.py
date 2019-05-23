import os

import slack

from slacky_emoji_control import EmojiControl
from slacky_block_builder import SlackyBlockBuilder
import config as cfg

import utilities as ut

import requests as r


class Slacky:

    def __init__(self):

        # Setup connection with Slack Workspace
        self.token = os.environ['SLACK_API_TOKEN']
        self.client = slack.WebClient(token=self.token)

        # Slacky internal setup
        self.ec = EmojiControl(self.client)
        self.bb = SlackyBlockBuilder(self.ec)

        # Get channels in workspace
        self.channels = self.get_channels()

    def __del__(self):

        # Clean-up
        ut.remove_directory_and_contents('tmp')

    def test(self, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)


        response_list = self.client.api_call(
            f'files.list?'
            f'count=1000&'
        )

        print(response_list['files'][-4])



        blocks = [
            {
                "type": "image",
                "image_url": f"{response_list['files'][-4]['url_private']}?pub_secret={response_list['files'][-4]['permalink_public'].split('-')[-1]}",
                "alt_text": f"{response_list['files'][-4]['id']}"
            }
        ]

        print(blocks)

        response = self.client.api_call(
            f'chat.postMessage?'
            f'as_user={cfg.POST["as_user"]}&'
            f'channel={channel_id}&'
            f'blocks={blocks}'
        )
        print(response)

    def format(self, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        messages = self.get_messages(channel_id=channel_id)
        if not messages:
            return

        message_payloads = self.bb.parse(messages)

        self.ec.parse()

        for messages_payload in message_payloads:
            timestamp = self.send_placeholder(channel_id=channel_id)
            if messages_payload['parent_blocks']:
                self.send_update(timestamp, messages_payload['parent_blocks'], channel_id=channel_id)
            if messages_payload['files']:
                self.send_reply(timestamp, messages_payload['files'], channel_id=channel_id)

        self.delete_set_messages(messages, channel_id=channel_id)

    def get_channels(self):
        """Returns a list of channels in the workspace
        Required Slack API Scopes:
            channels:read
            groups:read
        """
        response = self.client.api_call(
            f'conversations.list?types={cfg.CHANNEL["types"]}&exclude_archived={cfg.CHANNEL["exclude_archived"]}'
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
            f'conversations.history?channel={channel_id}'
        )
        assert response['ok']

        messages = []

        for message in response['messages']:
            thread_response = self.client.api_call(
                f'conversations.replies?'
                f'channel={channel_id}&'
                f'ts={message["ts"]}'
            )
            assert thread_response['ok']
            messages.extend(thread_response['messages'])
        return messages

    def send_message(self, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)
        response = self.client.api_call(
            f'chat.postMessage?'
            f'as_user={cfg.POST["as_user"]}&'
            f'channel={channel_id}&'
            'text=placeholder'
        )
        assert response['ok']
        return response['ts'], response['thread_ts']

    # def send_update(self, timestamp, blocks=None, text=None, channel_name=None, channel_id=None):
    #     if not channel_id:
    #         channel_id = self.find_channel_id(channel_name)
    #     data_type = 'blocks' if blocks else 'text'
    #     data = blocks if blocks else text
    #     response = self.client.api_call(
    #         f'chat.update?'
    #         f'as_user={cfg.POST["as_user"]}&'
    #         f'channel={channel_id}&'
    #         f'ts={timestamp}&'
    #         f'{data_type}={data}'
    #     )
    #     assert response['ok']

    # def send_reply(self, timestamp, files, channel_name=None, channel_id=None):
    #     if not channel_id:
    #         channel_id = self.find_channel_id(channel_name)
    #     for file in files:
    #         self.upload_file(file, timestamp, channel_id=channel_id)

    def upload_file(self, _file, timestamp, channel_name=None, channel_id=None):
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        file = {
            'file': (_file['path'], open(_file['path'], 'rb'))
        }

        upload_values = {
            "initial_comment": f'[{_file["category"]}] {_file["text"]}',
            "filename": _file['filename'],
            "token": self.token,
        }

        response_upload = ut.upload_file("https://slack.com/api/files.upload", file, upload_values)

        response = self.client.api_call(
            f'files.sharedPublicURL?'
            f'file={response_upload["file"]["id"]}'
        )
        assert response['ok']

        return f"{response['file']['url_private']}?pub_secret={response['file']['permalink_public'].split('-')[-1]}",

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

    def delete_set_messages(self, messages, channel_name=None, channel_id=None):
        self.delete_nuclear(
            channel_name=channel_name, channel_id=channel_id, messages=messages, confirmation_override=True
        )

    def delete_nuclear(
            self, channel_name=None, channel_id=None,
            messages=None, confirmation_override=False,
            restrict=None
    ):
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
        if not messages:
            messages = self.get_messages(channel_id=channel_id)
        for message in messages:
            if not restrict or (restrict['type'] in message and message[restrict['type']] in restrict['values']):
                if 'subtype' in message and message['subtype'] == 'tombstone':
                    continue
                if 'files' in message:
                    for file in message['files']:
                        response_delete = self.client.api_call(
                            f'files.delete?'
                            f'file={file["id"]}'
                        )
                        assert response_delete['ok']
                else:
                    response = self.client.api_call(
                        f'chat.delete?channel={channel_id}&ts={message["ts"]}'
                    )
                    assert response['ok']

    def remove_unused_files(self):
        response_list = self.client.api_call(
            f'files.list?'
            f'count=1000&'
        )
        assert response_list['ok']

        for file in [f for f in response_list['files'] if not f['channels'] and not f['groups'] and not f['ims']]:
            response_delete = self.client.api_call(
                f'files.delete?'
                f'file={file["id"]}'
            )
            assert response_delete['ok']
