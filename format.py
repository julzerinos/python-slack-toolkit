import sys

import re
from string import Template
import requests as rq
import os
import json

from googleapiclient.http import MediaFileUpload
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import config as cfg
import utilities as ut
from slacky.slacky import Slacky
from emoji_control.emoji_control import EmojiControl


def prepare_code_message(text):
    code = re.findall(r' `{3}([\s\S]*)`{3}', message['text'])[0]
    text = re.sub(r' (`{3}[\s\S]*`{3})', '', message['text'])
    extension = re.findall(r'^([^ ]*)', code)

    res = rq.post(
        'https://api.github.com/gists',
        auth = rq.auth.HTTPBasicAuth('julzerinos-bot', 'julzerinos123'),
        data = json.dumps(
            {
                'description': text,
                'files': {
                    f"file.{extension[0] if extension else 'txt'}": {
                        'content': code
                    }
                }
            })
        )

    if res.status_code == 201:
        return {
            'text': text,
            'url': res.json()['html_url']
            }


def prepare_link_message(message):
    url = re.findall(r'<(http[^<>]*)>', message['text'])[0]
    text = re.sub(r'<http([^<>]*)>', '', message['text'])

    print(text)

    if text == '' or text.isspace():
        text = message['attachments'][0]['fallback']

    return {
        'text': text,
        'url': url,
    }


def check_google_cred():
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def prepare_file_message(message):
    f = message['files'][0]
    path = ut.get_file(f)

    creds = check_google_cred()

    service = build('drive', 'v3', credentials=creds)
    
    file_created = service.files().create(
        body = {
            'name': f['id'],
            'copyRequiresWriterPermission': True
        },
        media_body = MediaFileUpload(path, f['mimetype']),
        fields = 'webViewLink, id, iconLink'
    ).execute()

    service.permissions().create(
        fileId = file_created['id'],
        body={
            'role': 'reader',
            'type': 'anyone'
        }
    ).execute()

    return {
        'text': message['text'],
        'url': file_created['webViewLink'],
        'url2': file_created['iconLink']
    }


def payload_str(msg, i=[0]):
    i[0] += 1
    if msg['content']['url'] is None:
        return f"{i[0]}\t{msg['content']['text']}"

    return f"{i[0]}\t<{msg['content']['url']}|:{msg['content']['emoji']}:>\t<{msg['content']['url']}|{ut.safe_format(msg['content']['text'])}>"

def iblock(msgs, category, msg_type):
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '\n'.join([payload_str(msg) for i, msg in enumerate(msgs)])
        },
        'block_id': f"{category}.{msg_type}.block"
    }

def tblock(type_):
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f"{cfg.CHT_CHR}\t_{type_}_"
        },
        'block_id': f"{category}.{type_}.type"
    }

def cblock(category):
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f"*{category}*"
        },
        'block_id': f"{category}.category"
    }

def dblock():
    return {
        "type": "divider"
    }


def get_categories(message):
    categories = re.findall(r'^\[([^\[\]]+)\]', message['text'])
    if 'text' in message and categories:
        categories = [cat.capitalize() for cat in categories[0].split(',')]
        message['text'] = re.sub(r'^\[([^\[\]]+)\]', '', message['text'])
    else:
        categories = ['General']
    return categories


def make_message(message):
    categories = get_categories(message)

    type_ = 'text'
    function = lambda x: {'text': x['text'], 'url': None}

    if 'files' in message:
        type_ = 'file'
        function = prepare_file_message
    elif re.findall(r' (`{3}[\s\S]*`{3})', message['text']):
        type_ = 'code'
        function = prepare_code_message 
    elif re.findall(r'<http([^<>]*)>', message['text']):
        type_ = 'link'
        function = prepare_link_message

    return {
        'type': type_,
        'content': function(message),
        'categories': categories
        }
    

def salvage(message):
    messages = dict()

    for block in [b for b in message['blocks'] if b['block_id'].split('.')[-1] == 'block']:
        if block['block_id'].split('.')[0] not in messages:
            messages[block['block_id'].split('.')[0]] = []
        for t in block['text']['text'].split('\n'):
            messages[block['block_id'].split('.')[0]].append(
                {
                    'type': block['block_id'].split('.')[1],
                    'content': {
                        'text': t.split('\t', 1)[1],
                        'url': None
                    },
                    
                }
            )

    return messages



def format(channel_id = None, channel_name = None):
    
    slacky = Slacky()
    ec = EmojiControl(slacky.client)

    channel_id = slacky.find_channel_id(channel_name)

    messages = slacky.get_messages(channel_id=channel_id, skip_non_user=True)
    if not messages:
        exit()

    pre_payload = dict()
    for message in reversed(messages):
        
        print(message)

        if 'bot_id' in message and 'blocks' in message:
            msgs = salvage(message)
            pre_payload.update(msgs)
            continue

        msg = make_message(message)

        if 'url2' in msg['content']:
            msg['content']['emoji'] = ec.get_emj_from_link(msg['content']['url2'], msg['content']['url2'].split('/')[-1])
        elif msg['content']['url'] is not None:
            msg['content']['emoji'] = ec.get_emj_from_favicon(msg['content']['url'])

        for category in msg['categories']:
            if category not in pre_payload:
                pre_payload[category] = []
            pre_payload[category].append(msg)

    payload = [dblock()]

    for category in pre_payload:
        payload.append(cblock(category))

        pre_payload[category].sort(key = lambda x: x['type'])
        types = set([t['type'] for t in pre_payload[category]])

        for t in types:
            payload.append(tblock(t))
            payload.append(iblock([msg for msg in pre_payload[category] if msg['type'] == t], category, t))

        payload.append(dblock())

    ec.parse()
    slacky.send_message(blocks=payload, channel_id=channel_id)

    slacky.delete_set_messages(messages, channel_id=channel_id)

    ut.cleanup()

