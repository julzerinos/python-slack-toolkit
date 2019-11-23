from flask import request

from slackflask import slackflask

from format import format


@slackflask.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        format("testing2")