import sys

from slacky.slacky import Slacky
from tools.slacky_master_controllers import SlackyBlockMaster, SlackyMessageMaster
from tools.slacky_emoji_control import EmojiControl

if __name__ == '__main__':
    slacky = Slacky()

    if len(sys.argv) > 2 and sys.argv[2] == 'nuclear':
        slacky.delete_messages(sys.argv[1])
        exit()

    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        print(slacky.upload_file('README.md', channel_name='testing2', timestamp=slacky.get_messages(channel_name='testing2')[0]['ts']))

        exit()

    channel_id = slacky.find_channel_id(sys.argv[1])

    messages = slacky.get_messages(channel_id=channel_id, skip_non_user=True)
    if not messages:
        exit()

    mm = SlackyMessageMaster()
    bm = SlackyBlockMaster()
    ec = EmojiControl(slacky.client)

    sorted_messages = dict()
    for msg in mm.parse(messages, ec):
        for category in msg.msg_catg:
            if category not in sorted_messages:
                sorted_messages[category] = []
            sorted_messages[category].append(msg)
    for catg, msgs in sorted_messages.items():
        sorted_messages[catg] = bm.parse(catg, msgs)
        for pht in sorted_messages[catg]['photos']:
            response = slacky.make_file_public(pht['alt_text'])
            pht['image_url'] = f"{response['file']['url_private']}?" \
                f"pub_secret={response['file']['permalink_public'].split('-')[-1]}"
            sorted_messages[catg]['blocks'].append(pht)
    ec.parse()
    for catg in sorted_messages:
        ts = slacky.send_message(blocks=sorted_messages[catg]['blocks'], channel_id=channel_id)
    slacky.delete_set_messages(messages, channel_id=channel_id)
