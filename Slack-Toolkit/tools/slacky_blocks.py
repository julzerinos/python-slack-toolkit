from datetime import datetime


def category_block():
    return [

    ]


def divider_block():
    return {
        "type": "divider"
    }


def category_title_block(title, block_id):
    x = 26 if len(title) % 2 else 25
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f'───── {title.center(x, " ")} ─────'
        },
        'block_id': block_id
    }


def text_block(payload, block_id):
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': payload,
        },
        'block_id': block_id
    }


def fields_block(payload, block_id):
    return {
            'type': 'section',
            "fields": payload,
            'block_id': block_id
        }


def photo_block(fid, block_id, text, url='n/a'):
    return {
            "type": "image",
            "image_url": url,
            "alt_text": fid,
            "block_id": block_id,
            "title": {
                'type': 'plain_text',
                'text': text
            }
        }


def date_block():
    return {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Last updated: {datetime.now().date()}"
            }
        ]

    }