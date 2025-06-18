import sys
import traceback

from fish.bot.twitch_bot import TwitchBot

import os


if __name__ == '__main__':

    try:
        bot = TwitchBot()
        bot.run()
    except:
        print("Unexpected error:", traceback.format_exc())
        sys.exit(1)