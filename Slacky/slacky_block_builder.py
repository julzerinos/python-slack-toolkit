import re
from string import Template
from urllib.parse import quote
import roman_numerals as rm

import config as cfg
import slacky_blocks as sb

import utilities as ut


class SlackyBlockBuilder:

    def __init__(self):
        self.link_messages = []
        self.text_messages = []
        self.photo_messages = []

    def parse(self, messages):
        self.message_type_switch(messages)
        return self.stack_blocks()

    def stack_blocks(self):
        parent_blocks = []
        files = []

        if self.link_messages:
            parent_blocks.append(
                sb.text_block(
                    self.prepare_link_payload(),
                    'LB'
                )
            )

        if self.text_messages:
            parent_blocks.append(
                sb.text_block(
                    self.prepare_text_payload(),
                    'TB'
                )
            )

        if self.photo_messages:
            files.extend(self.photo_messages)

        return parent_blocks, files

    def prepare_text_payload(self):
        return quote(
            '\n'.join([
                t_str.substitute(riter=rm.convert_to_numeral(i + 1)) for i, t_str in enumerate(self.text_messages)
            ])
        )

    def prepare_link_payload(self):
        return quote(
            '\n'.join([
                t_str.substitute(iter=str(i + 1).zfill(3)) for i, t_str in enumerate(self.link_messages)
            ])
        )

    def message_type_switch(self, messages):
        for message in messages:
            print(message)
            if not isinstance(message, dict):
                continue
            if 'subtype' in message and message['subtype'] in cfg.SUBTYPES:
                continue

            if 'bot_id' in message and 'blocks' in message:
                self.intercept_bot_message(message['blocks'])
                continue
            if 'files' in message:
                self.file_manager(message)
                continue
            if re.findall('<http([^<>]*)>', message['text']):
                self.create_link_message(message)
                continue
            self.create_text_message(message)

    def intercept_bot_message(self, blocks):
        for block in blocks:
            if 'LB' in block['block_id']:
                self.salvage_bot_link(block['text']['text'])
            if 'TB' in block['block_id']:
                self.salvage_bot_text(block['text']['text'])

    def salvage_bot_link(self, link_message):
        for link in link_message.split('\n'):
            self.link_messages.append(self.format_link_message(formatted_message=link.split('\t', 1)[1]))

    def salvage_bot_text(self, text_message):
        for text in text_message.split('\n'):
            self.text_messages.append(self.format_text_message(text.split('\t', 1)[1]))

    def create_text_message(self, message):
        self.text_messages.append(self.format_text_message(message['text']))

    def format_text_message(self, text):
        text = text.replace('\n', ' ')
        return Template(f"$riter\t{text}")

    def create_link_message(self, message):
        links = re.findall(r'<(http[^<>]*?)(?:\||>)', message['text'])
        text = re.sub(r'(<.*>)', '', message['text'])
        if not text and 'attachments' in message and message['attachments'][0]['fallback']:
            print(message['attachments'][0]['fallback'])
            text = ut.safe_format(message['attachments'][0]['fallback'])
        for link in links:
            self.link_messages.append(self.format_link_message(text, link=link))

    def format_link_message(self, text=None, link=None, formatted_message=None):
        if formatted_message:
            return Template(f"*{'$iter'}*\t{formatted_message}")
        return Template(f"*{'$iter'}*\t<{link}|:link:>\t{f'_{text}_' if text else link}")

    def file_manager(self, message):
        for file in message['files']:
            if file['filetype'] in cfg.IMG_FRM:
                self.image_manager(file)
            else:
                print('is other file')

    def image_manager(self, image):
        path = ut.get_file(image)
        self.photo_messages.append(self.create_photo_message(image, path))

    def create_photo_message(self, image, path):
        return {
            'filename': image['title'],
            'path': path
        }


