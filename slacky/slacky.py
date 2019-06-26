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
        together with the replies to each message

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

    def send_message(
            self, text=None, blocks=None, attachments=None,
            timestamp=None, channel_name=None, channel_id=None):
        """Posts a message in the channel with supplied content.
        If timestamp is provided, the message is sent as a reply

        Required Slack API Scopes:
            bot
            chat:write:user
            chat:write:bot
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        response = self.client.api_call(
            ''.join(
                [
                    f'chat.postMessage?as_user={cfg.POST["as_user"]}&channel={channel_id}&',
                    f'thread_ts={timestamp}&' if timestamp else '',
                    f'text={text}&' if text else '',
                    f'blocks={blocks}&' if blocks else '',
                    f'attachments={attachments}' if attachments else ''
                ]
            )
        )
        assert response['ok']
        return response

    def send_update(self, timestamp, text=None, blocks=None, attachments=None, channel_name=None, channel_id=None):
        """Updates a specified message by replacement

        Required Slack API Scopes:
            bot
            chat:write:user
            chat:write:bot
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        response = self.client.api_call(
            ''.join(
                [
                    f'chat.update?as_user={cfg.POST["as_user"]}&channel={channel_id}&ts={timestamp}&',
                    f'text={text}&' if text else '',
                    f'blocks={blocks}&' if blocks else '',
                    f'attachments={attachments}' if attachments else ''
                ]
            )
        )
        assert response['ok']
        return response

    def make_file_public(self, file_id):
        """Makes a file public, which generates a public permalink for the file

        Required Slack API Scopes:
            files:write:user
        """

        # Check if file is already public
        response = self.client.api_call(
            f'files.info?'
            f'file={file_id}'
        )
        if response['ok'] and response['file']['public_url_shared'] is True:
            return response

        response = self.client.api_call(
            f'files.sharedPublicURL?'
            f'file={file_id}'
        )
        assert response['ok']

        return response

    def make_file_private(self, file_id):
        """Makes a file private, revoking the public_permalink for the file

        Required Slack API Scopes:
            files:write:user
        """

        # Check if file is already private
        response = self.client.api_call(
            f'files.info?'
            f'file={file_id}'
        )
        if response['ok'] and response['file']['public_url_shared'] is False:
            return response

        response = self.client.api_call(
            f'files.revokePublicURL?'
            f'file={file_id}'
        )
        assert response['ok']

        return response

    def delete_messages(
            self, channel_name=None, channel_id=None,
            messages=None, confirmation_override=False,
            restrict=None, remove_files=True
    ):
        """Deletes all messages in a given channel
        Is used as a base for other delete methods

        Required Slack API Scopes:
            chat.delete
                bot
                chat:write:user
                chat:write:bot

            files.delete
                bot
                files:write:user
        """
        if not channel_id:
            channel_id = self.find_channel_id(channel_name)

        if not confirmation_override:
            confirmation = input(
                f"Are you sure you want to delete all messages from the channel #{channel_name}? Y/N\n")
            if 'Y' not in confirmation:
                print(f"Aborting delete on channel #{channel_name}")
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

                if remove_files and 'files' in message:
                    for file in message['files']:
                        response_delete = self.client.api_call(
                            f'files.delete?'
                            f'file={file["id"]}'
                        )
                        assert response_delete['ok']

    def delete_slack_generated(self, channel_name=None, channel_id=None):
        """Delete informational messages generated by slackbot"""
        self.delete_messages(
            channel_name=channel_name, channel_id=channel_id, confirmation_override=True,
            restrict={'type': 'subtype', 'values': cfg.SUBTYPES}
        )

    def delete_bot_messages(self, channel_name=None, channel_id=None):
        """Delete messages generated by any bot"""
        self.delete_messages(
            channel_name=channel_name, channel_id=channel_id, confirmation_override=True,
            restrict={'type': 'subtype', 'values': ['bot_message']}
        )

    def delete_set_messages(self, messages, channel_name=None, channel_id=None):
        """Delete a certain set of messages indicated by messages argument"""
        self.delete_messages(
            channel_name=channel_name, channel_id=channel_id, messages=messages, confirmation_override=True
        )

    def remove_unused_files(self):
        """Removes all files uploaded to a slack workspace,
        but not appearing in any channel, chat or group

        Required Slack API Scopes:
            files.list
                files:read

            files.delete
                bot
                files:write:user
        """

        response_list = self.client.api_call(
            f'files.list?'
            f'count=1000&'
        )
        assert response_list['ok']

        for file in [
            f for f in response_list['files']
            if not f['channels'] and not f['groups'] and not f['ims']
        ]:
            response_delete = self.client.api_call(
                f'files.delete?'
                f'file={file["id"]}'
            )
            assert response_delete['ok']
