import os
import slack


class Slacky:

    def __init__(self, channel):
        self.channel = channel
        self.token = os.environ['SLACK_API_TOKEN']
        self.client = slack.WebClient(token=self.token)

    def send_message(self):
        response = self.client.chat_postMessage(
            channel=self.channel,
            text='I yeeted and I yought.'
        )
        assert response['ok']

    def nuclear_delete(self):
        response = self.client.chat_delete(channel=self.channel, ts="*")
        assert response['ok']


slacky = Slacky('#testing')
slacky.send_message()
