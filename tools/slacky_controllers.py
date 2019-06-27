import re
from string import Template

import config as cfg
from utilities import MessageStruct, safe_format


def file_parse(message, categories):
    files = []
    for file in message['files']:
        if file['filetype'] in cfg.IMG_FRM:
            files.append(MessageStruct(
                'p',
                create_photo_message(file['name'], file['filetype'], file['id'], message['text']),
                categories
            ))
        else:
            files.append(
                create_file_message(file, message['text'], categories),
            )
    return files


def text_parse(message, categories, ec):
    if re.findall(r'(`{3}[\s\S]*`{3})', message['text']):
        return [create_code_message(message, categories)]

    if re.findall(r'<http([^<>]*)>', message['text']):
        return create_link_message(message, categories, ec)

    return [create_text_message(message, categories)]


def bot_parse(message):
    msgs = []
    for block in message['blocks']:
        block_id_values = block['block_id'].split('.')
        if 'links' in block_id_values[0]:
            msgs.extend(salvage_bot_link(block['text']['text'], block_id_values[-1]))
        if 'text' in block_id_values[0]:
            msgs.extend(salvage_bot_text(block['fields'], block_id_values[-1]))
        if 'prefor' in block_id_values[0]:
            msgs.append(salvage_bot_prefor(block['text']['text'], block_id_values[-1]))
        if 'phot' in block_id_values[0]:
            msgs.append(salvage_bot_photo(block, block_id_values[-1]))
        if 'files' in block_id_values[0]:
            msgs.extend(salvage_bot_file(block['text']['text'], block_id_values[-1]))
    return msgs


def salvage_bot_prefor(text, category):
    return MessageStruct(
        'c',
        format_code_message(text.split('\n\n', 1)[-1]),
        [category],
    )


def salvage_bot_text(fields, category):
    msgs = []
    for field in fields:
        msgs.append(MessageStruct(
            't',
            format_text_message(field['text'].split('\n\n')[-1]),
            [category],
        ))
    return msgs


def salvage_bot_link(link_message, category):
    msgs = []
    for link in link_message.split(cfg.MSG_SEP['lk']):
        msgs.append(MessageStruct(
            'l',
            format_link_message(formatted_message=link.split('\t', 1)[1]),
            [category],
        ))
    return msgs


def salvage_bot_photo(photo, category):
    return MessageStruct(
        'p',
        photo,
        [category]
    )


def salvage_bot_file(files_info, category):
    msgs = []
    for file in files_info.split(cfg.MSG_SEP['lk']):
        msgs.append(MessageStruct(
            'f',
            format_file_message('', '', formatted_text=file.split('\t', 1)[1]),
            [category],
        ))
    return msgs


def create_link_message(message, categories, ec):
    msgs = []
    links = re.findall(r'<(http[^<>]*?)(?:\||>)', message['text'])
    text = re.sub(r'(<.*>)', '', message['text'])
    if (not text or text.isspace()) and 'attachments' in message and message['attachments'][0]['fallback']:
        text = safe_format(message['attachments'][0]['fallback'])
    for link in links:
        msgs.append(MessageStruct(
            'l',
            format_link_message(text, link=link, ec=ec),
            categories,
        ))
    return msgs


def create_text_message(message, categories):
    return MessageStruct(
        't',
        format_text_message(message['text']),
        categories,
    )


def create_code_message(message, categories):
    return MessageStruct(
        'c',
        format_code_message(message['text']),
        categories,
    )


def create_photo_message(filename, filetype, fileid, text):
    return {
        'filename': filename,
        'filetype': filetype,
        'file_id': fileid,
        'text': Template(
            'Image $iter'
            if text.isspace() or text == ''
            else f'Image $iter: {text}'
        ),
    }


def create_file_message(file, text, categories):
    return MessageStruct(
        'f',
        format_file_message(file, text),
        categories
    )


def format_text_message(text):
    return Template(f'{cfg.CHT_CHR}​\n*-- $iter --*\n\n{text}')


def format_link_message(text=None, link=None, formatted_message=None, ec=None):
    if formatted_message:
        return Template(f"{'$iter'}\t{formatted_message}")
    emoji = ec.get_emj_from_favicon(link) if ec else 'link'
    return Template(f"{'$iter'}\t<{link}|:{emoji}:>\t<{link}|_{text if text else emoji}_>")


def format_code_message(text):
    return Template(f'`$iter`\n\n{text}')


def format_file_message(file, text, formatted_text=None):
    if formatted_text:
        return Template(f"{'$iter'}\t{formatted_text}")
    return Template(
        f"{'$iter'}\t"
        f"`.{file['filetype']}`\t"
        f"<{file['url_private']}|_{file['name'] if text.isspace() or text == '' else text}_>"
    )
