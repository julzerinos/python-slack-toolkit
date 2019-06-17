import sys

from slacky import Slacky

if __name__ == '__main__':
    slacky = Slacky()

    if len(sys.argv) > 2 and sys.argv[2] == 'nuclear':
        slacky.delete_nuclear(sys.argv[1])
        exit()

    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        slacky.test(sys.argv[1])
        exit()

    slacky.format(sys.argv[1])
