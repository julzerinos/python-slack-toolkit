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
