import os

import tldextract
import requests as r


class EmojiControl:
    def __init__(self, client, token=None):
        self.client = client

        self.token = token if token else os.environ["SLACK_USER_TOKEN"]

        self.current_list = self.get_current_emoji()
        self.new_list = []

    def get_current_emoji(self):
        """Retrieves the current list of emoji in the workspace.

        Returns a list of existing emoji objects.

        Required Slack API Scopes:
            user:emoji:read
        """
        response = self.client.api_call(
            f'emoji.list?'
        )
        assert response['ok']
        return response['emoji']

    def parse(self):
        """Sends emoji collected in self.new_list if it is not in workspace."""
        for emoji in self.new_list:
            if emoji['name'] not in self.current_list:
                self.send_new_emoji(emoji)
                self.new_list.remove(emoji)

    def send_new_emoji(self, emoji):
        """Posts the new emoji to the slack api call.

        Emoji object must be a dictionary with
            name key - name of the emoji
            content key - the content in binary form

        The user token is required here.
        """
        headers = {
            'Authorization': f'Bearer {self.token}',
        }

        files = {
            'image': (
                '_',
                emoji['content']
            ),
        }
        params = {
            'name': emoji['name'],
            'mode': 'data'
        }

        response = r.post('https://slack.com/api/emoji.add', headers=headers, files=files, params=params).json()

        assert response['ok']

    def get_emj_from_link(self, link, name):
        """Gets the binary content of an emoji from a link."""
        response = r.get(url=link)

        self.new_list.append(
            {
                'name': name,
                'content': response.content
                }
        )
        return name

    def get_emj_from_favicon(self, link):
        """Gets the favicon of a website as the emoji.

        The emoji name is the domain of the page.
        """
        name = tldextract.extract(link).domain

        self.get_emj_from_link(
            f'https://www.google.com/s2/favicons?domain={link}',
            name=name
        )

        return name

    def get_emj_from_file(self, filepath, name=None):
        """Gets the binary content of an emoji from a file."""
        self.new_list.append(
            {
                'name': name if name else os.path.basename(filepath),
                'content': open(filepath, 'rb')
            }
        )
