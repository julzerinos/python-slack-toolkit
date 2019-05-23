import sys

from slacky import Slacky

if __name__ == '__main__':
    slacky = Slacky()
    # slacky.delete_nuclear(sys.argv[1])
    # slacky.delete_slack_generated(sys.argv[1])
    # slacky.delete_bot_messages(sys.argv[1])

    # print(slacky.get_messages(sys.argv[1]))

    if len(sys.argv) > 2 and sys.argv[2] == 'nuclear':
        slacky.delete_nuclear(sys.argv[1])
        exit()

    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        slacky.test(sys.argv[1])
        exit()

    slacky.format(sys.argv[1])
