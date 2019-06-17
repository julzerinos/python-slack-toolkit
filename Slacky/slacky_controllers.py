import re
from string import Template

import config as cfg
from utilities import MessageStruct, safe_format


class FileControl:
    def parse(self, message, categories):
        text = message['text']
        for file in message['files']:
            if file['filetype'] in cfg.IMG_FRM:
                return MessageStruct(
                    'p',
                    create_photo_message(file, text),
                    categories
                )
            else:
                return MessageStruct(
                    'f',
                    create_file_message(file, text),
                    categories
                )


class TextControl:
    def __init__(self, ec):
        self.ec = ec

    def parse(self, message, categories):
        if re.findall(r'(`{3}[\s\S]*`{3})', message['text']):
            return [self.create_prefor_message(message, categories)]

        if re.findall(r'<http([^<>]*)>', message['text']):
            return self.create_link_message(message, categories)

        return [self.create_text_message(message, categories)]

    @staticmethod
    def create_text_message(message, categories):
        return MessageStruct(
            't',
            format_text_message(message['text']),
            categories,
        )

    def create_link_message(self, message, categories):
        msgs = []
        links = re.findall(r'<(http[^<>]*?)(?:\||>)', message['text'])
        text = re.sub(r'(<.*>)', '', message['text'])
        if (not text or text.isspace()) and 'attachments' in message and message['attachments'][0]['fallback']:
            text = safe_format(message['attachments'][0]['fallback'])
        for link in links:
            msgs.append(MessageStruct(
                'l',
                format_link_message(text, link=link, ec=self.ec),
                categories,
            ))
        return msgs

    @staticmethod
    def create_prefor_message(message, categories):
        return MessageStruct(
            'c',
            format_code_message(message['text']),
            categories,
        )


class BotMessageControl:
    def parse(self, message):
        msgs = []
        for block in message['blocks']:
            block_id_values = block['block_id'].split('.')
            if 'links' in block_id_values[0]:
                msgs.extend(self.salvage_bot_link(block['text']['text'], block_id_values[-1]))
            if 'text' in block_id_values[0]:
                msgs.extend(self.salvage_bot_text(block['fields'], block_id_values[-1]))
            if 'prefor' in block_id_values[0]:
                msgs.append(self.salvage_bot_prefor(block['text']['text'], block_id_values[-1]))
        return msgs

    @staticmethod
    def salvage_bot_link(link_message, category):
        msgs = []
        for link in link_message.split(cfg.MSG_SEP['lk']):
            msgs.append(MessageStruct(
                'l',
                format_link_message(formatted_message=link.split('\t', 1)[1]),
                [category],
            ))
        return msgs

    @staticmethod
    def salvage_bot_text(fields, category):
        msgs = []
        for field in fields:
            msgs.append(MessageStruct(
                't',
                format_text_message(field['text'].split('\n\n')[-1]),
                [category],
            ))
        return msgs

    @staticmethod
    def salvage_bot_prefor(text, category):
        return MessageStruct(
            'c',
            format_code_message(text.split('\n\n', 1)[-1]),
            [category],
        )


def format_text_message(text):
    return Template(f'{cfg.CHT_CHR}​\n*-- $iter --*\n\n{text}')


def format_link_message(text=None, link=None, formatted_message=None, ec=None):
    if formatted_message:
        return Template(f"{'$iter'}\t{formatted_message}")
    emoji = ec.get_favicon_from_link(link) if ec else 'link'
    return Template(f"{'$iter'}\t<{link}|:{emoji}:>\t{f'_{text}_' if text else emoji}")


def format_code_message(text):
    return Template(f'`$iter`\n\n{text}')


def create_photo_message(file, text):
    return {
        'filename': file['name'],
        'filetype': file['filetype'],
        'file_id': file['id'],
        'text': text,
    }


def create_file_message(file, text):
    return {
        'filename': file['name'],
        'filetype': file['filetype'],
        'file_id': file['id'],
        'text': text,
    }
