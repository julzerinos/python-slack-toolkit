import tldextract
import requests as r

from grabicon import FaviconGrabber

import utilities as ut
import os


class EmojiControl:
    def __init__(self, client):
        self.client = client
        self.grabber = FaviconGrabber()

        self.current_list = self.get_current_emoji()
        self.new_list = []

    def get_current_emoji(self):
        response = self.client.api_call(
            f'emoji.list?'
        )
        assert response['ok']
        return response['emoji']

    def parse(self):
        for emoji in self.new_list:
            if emoji['domain'] not in self.current_list:
                self.send_new_emoji(emoji)
        ut.remove_directory_and_contents('tmp')

    def send_new_emoji(self, emoji):
        headers = {
            'Authorization': f'Bearer {os.environ["SLACK_USER_TOKEN"]}',
        }

        files = {
            'image': (
                emoji['path'],
                open(emoji['path'], 'rb')
            ),
        }
        params = {
            'name': emoji['domain'],
            'mode': 'data'
        }

        response = r.post('https://slack.com/api/emoji.add', headers=headers, files=files, params=params).json()
        assert response['ok']

    def get_favicon_from_link(self, link):
        name = tldextract.extract(link).domain

        response = r.get(
            url=f'https://www.google.com/s2/favicons?domain={link}'
        )

        path = f'tmp/icon/{name}.png'
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as i:
            i.write(response.content)

        self.new_list.append(
            {'domain': name, 'path': path}
        )
        return name
