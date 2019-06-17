import re
from string import Template

import config as cfg


class FileControl:
    def __init__(self):
        self.messages = []

    def parse(self):
        for message in self.messages:
            self.file_manager(message['message'], message['categories'])

    def file_manager(self, message, categories):
        text = message['text']
        for category in categories:
            for file in message['files']:
                if file['filetype'] in cfg.IMG_FRM:
                    self.categories[category]['file_messages'].append(
                        self.create_photo_message(file, text, category)
                    )
                else:
                    self.categories[category]['file_messages'].append(
                        self.create_file_message(file, text, category)
                    )

    def create_photo_message(self, file, text, category):
        return {
            'type': 'p',
            'filename': file['name'],
            'filetype': file['filetype'],
            'file_id': file['id'],
            'text': text,
            'category': category,
            'block': sb.photo_block(fid=file['id'])
        }

    def create_file_message(self, file, text, category):
        return {
            'type': 'f',
            'filename': file['name'],
            'filetype': file['filetype'],
            'file_id': file['id'],
            'text': text,
            'category': category,
            'block': sb.text_block()
        }


class TextControl:
    def __init__(self, ec):
        self.ec = ec
        self.messages = []

    def parse(self):
        for message in self.messages:
            if re.findall(r'(`{3}[\s\S]*`{3})', message['text']):
                self.create_prefor_message(message['message'], message['categories'])
                continue
            if re.findall(r'<http([^<>]*)>', message['text']):
                self.create_link_message(message['message'], message['categories'])
                continue
            self.create_text_message(message['message'], message['categories'])

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
