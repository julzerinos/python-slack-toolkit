import re
from string import Template
from urllib.parse import quote
import numeral as num

import config as cfg
import slacky_blocks as sb

import utilities as ut


class CategoryException(BaseException):
    pass


class SlackyBlockBuilder:

    def __init__(self, ec):
        self.ec = ec

        self.categories = {
            'General': {
                'link_messages': [],
                'text_messages': [],
                'file_messages': [],
                'prefor_messages': []
            }
        }

    def create_category(self, categories):
        for category in categories:
            if category not in self.categories:
                self.categories[category] = {
                    'link_messages': [],
                    'text_messages': [],
                    'file_messages': [],
                    'prefor_messages': []
                }

    def is_category_empty(self, category):
        if not self.categories[category]['link_messages'] \
                and not self.categories[category]['text_messages'] \
                and not self.categories[category]['file_messages'] \
                and not self.categories[category]['prefor_messages']:
            return True

    def parse(self, messages):
        self.message_type_switch(messages)
        return self.prepare_final_payload()

    def prepare_final_payload(self):
        categories = []
        for category in [cat for cat in self.categories if not self.is_category_empty(cat)]:
            categories.append(self.category_stack_blocks(category))
        categories.sort(key=lambda x: len(x['files']))
        return categories

    def category_stack_blocks(self, category):
        parent_blocks = []
        files = []

        parent_blocks.append(
            sb.category_title_block(category, f'title.{category}')
        )

        if self.categories[category]['link_messages']:
            parent_blocks.append(
                sb.text_block(
                    self.prepare_link_payload(category),
                    f'links.{category}'
                )
            )

        if self.categories[category]['prefor_messages']:
            for i, message in enumerate(self.prepare_prefor_payload(category)):
                parent_blocks.append(
                    sb.text_block(
                        message,
                        f'prefor{i}.{category}'
                    )
                )

        if self.categories[category]['text_messages']:
            for i, payload in enumerate([self.prepare_text_payload(category)[x:x + 10] for x in
                                         range(0, len(self.prepare_text_payload(category)), 10)]):
                parent_blocks.append(
                    sb.fields_block(
                        payload,
                        f'text{i}.{category}'
                    )
                )

        if self.categories[category]['file_messages']:
            self.prepare_file_payload(category)
            files.extend(self.categories[category]['file_messages'])

        return {
            'parent_blocks': parent_blocks,
            'files': files
        }

    def prepare_text_payload(self, category):
        return [
            {
                'type': 'mrkdwn',
                'text': text.substitute(iter=num.int2roman(i + 1))
            }
            for i, text in enumerate(self.categories[category]['text_messages'])
        ]

    def prepare_link_payload(self, category):
        return quote(
            cfg.MSG_SEP['lk'].join([
                t_str.substitute(iter=str(i + 1).zfill(3)) for i, t_str in
                enumerate(self.categories[category]['link_messages'])
            ])
        )

    def prepare_prefor_payload(self, category):
        return [
            text.substitute(iter=num.int2letter(i))
            for i, text in enumerate(self.categories[category]['prefor_messages'])
        ]

    def prepare_file_payload(self, category):
        self.categories[category]['file_messages'].sort(key=lambda x: x['filetype'])

    def message_type_switch(self, messages):
        for message in messages:
            if not isinstance(message, dict):
                continue
            if 'subtype' in message and message['subtype'] in cfg.SUBTYPES:
                continue

            if 'bot_id' in message and 'blocks' in message:
                self.intercept_bot_message(message['blocks'])
                continue

            message_categories = []
            if 'text' in message and re.findall(r'\[([^\[\]]+)\]', message['text']):
                message_categories = [cat.capitalize() for cat in re.findall(r'\[([^\[\]]+)\]', message['text'])]
                message['text'] = re.sub(r'\[([^\[\]]+)\]', '', message['text'])
            if message_categories:
                self.create_category(message_categories)
            else:
                message_categories = ['General']

            if 'files' in message:
                self.file_manager(message, message_categories)
                continue
            if re.findall(r'(`{3}[\s\S]*`{3})', message['text']):
                self.create_prefor_message(message, message_categories)
                continue
            if re.findall(r'<http([^<>]*)>', message['text']):
                self.create_link_message(message, message_categories)
                continue
            self.create_text_message(message['text'], message_categories)

    def intercept_bot_message(self, blocks):
        for block in blocks:
            block_id_values = block['block_id'].split('.')
            self.create_category([block_id_values[-1]])
            if 'links' in block_id_values[0]:
                self.salvage_bot_link(block['text']['text'], block_id_values[-1])
            if 'text' in block_id_values[0]:
                self.salvage_bot_text(block['fields'], block_id_values[-1])
            if 'prefor' in block_id_values[0]:
                self.salvage_bot_prefor(block['text']['text'], block_id_values[-1])


    def salvage_bot_link(self, link_message, category):
        for link in link_message.split(cfg.MSG_SEP['lk']):
            self.categories[category]['link_messages'].append(
                self.format_link_message(formatted_message=link.split('\t', 1)[1]))

    def salvage_bot_text(self, fields, category):
        for field in fields:
            self.categories[category]['text_messages'].append(self.format_text_message(field['text'].split('\n\n')[-1]))

    def salvage_bot_prefor(self, text, category):
        self.categories[category]['prefor_messages'].append(self.format_prefor_message(text.split('\n\n', 1)[-1]))

    def create_text_message(self, message, categories):
        if message == '':
            return
        for category in categories:
            self.categories[category]['text_messages'].append(self.format_text_message(message))

    def format_text_message(self, text):
        return Template(f'{cfg.CHT_CHR}​\n`$iter`\n\n{text}')

    def create_link_message(self, message, categories):
        for category in categories:
            links = re.findall(r'<(http[^<>]*?)(?:\||>)', message['text'])
            text = re.sub(r'(<.*>)', '', message['text'])
            if (not text or text.isspace()) and 'attachments' in message and message['attachments'][0]['fallback']:
                text = ut.safe_format(message['attachments'][0]['fallback'])
            for link in links:
                self.categories[category]['link_messages'].append(self.format_link_message(text, link=link))

    def format_link_message(self, text=None, link=None, formatted_message=None):
        if formatted_message:
            return Template(f"{'$iter'}\t{formatted_message}")
        emoji = self.ec.get_favicon_from_link(link)
        return Template(f"{'$iter'}\t<{link}|:{emoji}:>\t{f'_{text}_' if text else emoji}")

    def create_prefor_message(self, message, categories):
        for catgory in categories:
            self.categories[catgory]['prefor_messages'].append(self.format_prefor_message(message['text']))

    def format_prefor_message(self, text):
        return Template(f'*$iter)*\n\n{text}')

    def file_manager(self, message, categories):
        text = message['text']
        for category in categories:
            for file in message['files']:
                self.categories[category]['file_messages'].append(
                    self.create_file_message(file, text, ut.get_file(file), category)
                )

    def create_file_message(self, file, text, path, category):
        return {
            'text': text,
            'filetype': file['filetype'],
            'filename': file['name'],
            'path': path,
            'category': category
        }
