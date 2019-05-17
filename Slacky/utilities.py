import re

import requests as r
import os

import unicodedata


def get_file(file):
    response = r.get(
        url=file['url_private'],
        headers={
            "Authorization": f"Bearer {os.environ['SLACK_API_TOKEN']}"},
        allow_redirects=False
    )

    path = f'tmp/photo/{file["timestamp"]}.{file["filetype"]}'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb') as i:
        i.write(response.content)

    return path


def safe_format(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """

    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return re.sub('[^\w\s-]', '', value.decode().strip())


def upload_file(file, upload_values):
    response = r.post("https://slack.com/api/files.upload", files=file, params=upload_values).json()
    assert response['ok']