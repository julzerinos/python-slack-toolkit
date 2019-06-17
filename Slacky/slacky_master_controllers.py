import re
from urllib.parse import quote
import numeral as num

import config as cfg
import slacky_blocks as sb

from slacky_controllers import FileControl, TextControl, BotMessageControl


class CategoryException(BaseException):
    pass


class SlackyMessageMaster:

    def __init__(self, ec):
        self.bc = BotMessageControl()
        self.fc = FileControl()
        self.tc = TextControl(ec)

        self.messages = []

    def parse(self, messages):
        for message in messages:
            if 'bot_id' in message and 'blocks' in message:
                self.messages.extend(self.bc.parse(message))
                continue

            if 'text' in message and re.findall(r'\[([^\[\]]+)\]', message['text']):
                categories = [cat.capitalize() for cat in re.findall(r'\[([^\[\]]+)\]', message['text'])]
                message['text'] = re.sub(r'\[([^\[\]]+)\]', '', message['text'])
            else:
                categories = ['General']

            self.messages.extend(
                self.fc.parse(message, categories)
                if 'files' in message
                else self.tc.parse(message, categories)
            )

        return self.messages


class SlackyBlockMaster:

    def parse(self, catg, catg_messages):
        msgs = dict()
        for msg in catg_messages:
            if msg.msg_type not in msgs:
                msgs[msg.msg_type] = []
            msgs[msg.msg_type].append(msg)

        parent_blocks = []
        files = []

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

        # if self.categories[catg]['file_messages']:
        #     self.prepare_file_payload(catg)
        #     files.extend(self.categories[catg]['file_messages'])

        return {
            'parent_blocks': parent_blocks,
            'files': files
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
