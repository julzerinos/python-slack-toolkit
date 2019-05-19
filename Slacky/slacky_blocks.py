from datetime import datetime


def divider_block():
    return {
        "type": "divider"
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
