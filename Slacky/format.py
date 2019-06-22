import sys

from slacky import Slacky

if __name__ == '__main__':
    slacky = Slacky()

    if len(sys.argv) > 2 and sys.argv[2] == 'nuclear':
        slacky.delete_nuclear(sys.argv[1])
        exit()

    channel_id = slacky.find_channel_id(sys.argv[1])

    messages = slacky.get_messages(channel_id=channel_id, skip_non_user=True)
    if not messages:
        exit()
    sorted_messages = dict()
    for msg in slacky.mm.parse(messages, slacky.ec):
        for category in msg.msg_catg:
            if category not in sorted_messages:
                sorted_messages[category] = []
            sorted_messages[category].append(msg)
    for catg, msgs in sorted_messages.items():
        sorted_messages[catg] = slacky.bm.parse(catg, msgs)
        for pht in sorted_messages[catg]['photos']:
            pht['image_url'] = slacky.make_file_public(pht['alt_text'])
            sorted_messages[catg]['blocks'].append(pht)
    slacky.ec.parse()
    for catg in sorted_messages:
        ts = slacky.send_message(sorted_messages[catg]['blocks'], channel_id=channel_id)
    slacky.delete_set_messages(messages, channel_id=channel_id)
