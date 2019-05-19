from datetime import datetime


def category_block():
    return [

    ]


def divider_block():
    return {
        "type": "divider"
    }


def category_title_block(title, block_id):
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': title,
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
