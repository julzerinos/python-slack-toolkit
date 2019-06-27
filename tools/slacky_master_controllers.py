import re
from urllib.parse import quote
import numeral as num

import config as cfg
import tools.slacky_blocks as sb
from tools.slacky_controllers import text_parse, file_parse, bot_parse


class SlackyMessageMaster:

    def __init__(self):
        self.messages = []

    def parse(self, messages, ec):
        for message in messages:
            print(message)
            if 'bot_id' in message and 'blocks' in message:
                self.messages.extend(bot_parse(message))
                continue

            categories = []
            if 'text' in message:
                categories, message['text'] = self.get_categories(message['text'])

            if not categories:
                categories = ['General']

            self.messages.extend(
                file_parse(message, categories)
                if 'files' in message
                else text_parse(message, categories, ec)
            )

        return self.messages

    @staticmethod
    def get_categories(text):
        tmp = re.findall(r'(```[\s\S]*?```)', text)
        text = re.sub(r'(```[\s\S]*?```)', '', text)
        categories = [cat.capitalize() for cat in re.findall(r'\[([^\[\]]+)\]', text)]
        return categories, ' '.join([text] + tmp)


class SlackyBlockMaster:

    def parse(self, catg, catg_messages):
        msgs = dict()
        for msg in catg_messages:
            if msg.msg_type not in msgs:
                msgs[msg.msg_type] = []
            msgs[msg.msg_type].append(msg)

        parent_blocks = []
        photos = []

        parent_blocks.append(
            sb.divider_block()
        )

        parent_blocks.append(
            sb.category_title_block(catg, f'title.{catg}')
        )

        if 'l' in msgs:
            parent_blocks.append(
                sb.text_block(
                    self.prepare_link_payload(msgs['l']),
                    f'links.{catg}'
                )
            )

        if 'c' in msgs:
            for i, message in enumerate(self.prepare_code_payload(msgs['c'])):
                parent_blocks.append(
                    sb.text_block(
                        message,
                        f'prefor{i}.{catg}'
                    )
                )

        if 't' in msgs:
            for i, payload in enumerate([
                self.prepare_text_payload(msgs['t'])[x:x + 10]
                for x in
                range(0, len(self.prepare_text_payload(msgs['t'])), 10)
            ]):
                parent_blocks.append(
                    sb.fields_block(
                        payload,
                        f'text{i}.{catg}'
                    )
                )

        if 'f' in msgs:
            parent_blocks.append(
                sb.text_block(
                    self.prepare_file_payload(msgs['f']),
                    f'files.{catg}'
                )
            )

        if 'p' in msgs:
            for i, pht in enumerate(msgs['p']):
                if 'type' in pht.msg_cont:
                    parent_blocks.append(
                        sb.photo_block(
                            pht.msg_cont['alt_text'],
                            f'phot{i}.{catg}',
                            re.sub(r'Image \d+', f'Image {i + 1}', pht.msg_cont['title']['text']),
                            pht.msg_cont['image_url']
                        )
                    )
                else:
                    photos.append(
                        sb.photo_block(
                            pht.msg_cont['file_id'],
                            f'phot{i}.{catg}',
                            pht.msg_cont['text'].substitute(iter=(i + 1))
                        )
                    )

        return {
            'blocks': parent_blocks,
            'photos': photos,
        }

    @staticmethod
    def prepare_text_payload(msgs):
        return [
            {
                'type': 'mrkdwn',
                'text': stc.msg_cont.substitute(iter=num.int2letter(i))
            }
            for i, stc in enumerate(msgs)
        ]

    @staticmethod
    def prepare_link_payload(msgs):
        return quote(
            cfg.MSG_SEP['lk'].join([
                stc.msg_cont.substitute(iter=str(i + 1).zfill(3))
                for i, stc in enumerate(msgs)
            ])
        )

    @staticmethod
    def prepare_code_payload(msgs):
        return [
            stc.msg_cont.substitute(iter=num.int2roman(i + 1))
            for i, stc in enumerate(msgs)
        ]

    @staticmethod
    def prepare_file_payload(msgs):
        return quote(
            cfg.MSG_SEP['lk'].join([
                stc.msg_cont.substitute(iter=str(i + 1).zfill(3))
                for i, stc in enumerate(msgs)
            ])
        )
