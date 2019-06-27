import re
import unicodedata
import string

import requests as r

import os
import shutil

import config as cfg

from dataclasses import dataclass


@dataclass
class MessageStruct:
    msg_type: str
    msg_cont: object
    msg_catg: list


def get_file(file):
    response = r.get(
        url=file['url_private'],
        headers={
            "Authorization": f"Bearer {os.environ['SLACK_API_TOKEN']}"
        },
        allow_redirects=False
    )

    path = f'tmp/file/{file["timestamp"]}.{file["filetype"]}'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb') as i:
        i.write(response.content)

    return path


def post(url, file=None, params=None, headers=None, body=None):
    response = r.post(url=url, files=file, params=params, headers=headers, data=body).json()
    assert response['ok']
    return response


def safe_format(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """

    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return re.sub(r'[^\w\s-]', '', value.decode().strip())


def remove_directory_and_contents(directory):
    if not os.path.isdir(directory):
        return
    shutil.rmtree(directory, ignore_errors=False)
