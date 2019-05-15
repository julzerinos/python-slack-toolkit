# Settings for get_channels
CHANNEL = dict(
    exclude_archived='true',
    types='public_channel,private_channel'
)

# Settings for postMessage
POST = dict(
    as_user='false'
)

# Slack channel information message subtypes
SUBTYPES = [
    'channel_archive', 'channel_join', 'channel_leave', 'channel_name', 'channel_purpose',
    'channel_topic', 'channel_unarchive', 'ekm_access_denied', 'file_comment', 'file_mention', 'file_share',
    'group_archive', 'group_join', 'group_leave', 'group_name', 'group_purpose', 'group_topic',
    'group_unarchive', 'me_message', 'message_changed', 'message_deleted', 'message_replied', 'pinned_item',
    'reply_broadcast', 'thread_broadcast', 'unpinned_item'
]

# Acceptable image formats
IMG_FRM = [
    'jpg', 'png'
]
