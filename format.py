import sys

from slacky.slacky import Slacky
from tools.slacky_master_controllers import SlackyBlockMaster, SlackyMessageMaster
from emoji_control.emoji_control import EmojiControl

if __name__ == '__main__':
    slacky = Slacky()

    if len(sys.argv) > 2 and sys.argv[2] == 'nuclear':
        slacky.delete_messages(sys.argv[1])
        exit()

    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        ec = EmojiControl(slacky.client)
        ec.get_emj_from_link('https://scontent.fwaw3-1.fna.fbcdn.net/v/t34.18173-12/26694531_1964543693873363_371642509_n.jpg?_nc_cat=102&_nc_oc=AQks4MDOqpkyB9Cfh254BEdM6W6Af96Oa9OQhAr2Ai-iIZb_MfhQCImQwHilWeB1H3c&_nc_ht=scontent.fwaw3-1.fna&oh=7208f0f344bf670148f84336091f2bb1&oe=5D16CEF6', 'bóg')
        ec.parse()
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
