import sys

from slacky import Slacky

if __name__ == '__main__':
    slacky = Slacky()
    # slacky.delete_nuclear(sys.argv[1])
    # slacky.delete_slack_generated(sys.argv[1])
    #slacky.delete_bot_messages(sys.argv[1])

    slacky.parse(sys.argv[1])
