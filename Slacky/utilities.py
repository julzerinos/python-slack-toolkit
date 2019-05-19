import re

import requests as r
import os

import unicodedata


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


def upload_file(url, file=None, upload_values=None, headers=None, body=None):
    response = r.post(url=url, files=file, params=upload_values, headers=headers, data=body).json()
    assert response['ok']


def safe_format(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """

    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return re.sub(r'[^\w\s-]', '', value.decode().strip())
