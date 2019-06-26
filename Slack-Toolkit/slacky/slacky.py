import os

import slack

import config as cfg


class Slacky:

    def __init__(self):
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

    def get_messages(self, channel_name=None, channel_id=None, skip_non_user=False):
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
            if skip_non_user and 'subtype' in message and message['subtype'] in cfg.SUBTYPES:
                continue

            thread_response = self.client.api_call(
                f'conversations.replies?'
                f'channel={channel_id}&'
                f'ts={message["ts"]}'
            )
            assert thread_response['ok']
            messages.extend(thread_response['messages'])
        return messages

    def send_message(self, text=None, blocks=None, attachments=None, channel_name=None, channel_id=None):
        """Posts a message in the channel with supplied content
        Required Slack API Scopes:
            bot
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        response = self.client.api_call(
            ''.join(
                [
                    f'chat.postMessage?as_user={cfg.POST["as_user"]}&channel={channel_id}&',
                    f'text={text}' if text else '',
                    f'blocks={blocks}' if blocks else '',
                    f'attachments={attachments}' if attachments else ''
                ]
            )
        )
        assert response['ok']
        return response

    def make_file_public(self, file_id):
        response = self.client.api_call(
            f'files.info?'
            f'file={file_id}'
        )
        if response['ok'] and response['file']['public_url_shared'] is True:
            return f"{response['file']['url_private']}?pub_secret={response['file']['permalink_public'].split('-')[-1]}"

        response = self.client.api_call(
            f'files.sharedPublicURL?'
            f'file={file_id}'
        )
        assert response['ok']

        return f"{response['file']['url_private']}?pub_secret={response['file']['permalink_public'].split('-')[-1]}"

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

        for file in [
            f for f in response_list['files']
            if not f['channels'] and not f['groups'] and not f['ims']
               and not f['permalink_public']
        ]:
            response_delete = self.client.api_call(
                f'files.delete?'
                f'file={file["id"]}'
            )
            assert response_delete['ok']
