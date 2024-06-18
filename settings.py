import os


BATHE_PATH = os.path.dirname(os.path.realpath(__file__))
SAVER_DEFAULT_PATH = os.path.join(BATHE_PATH, "_Data")
SAVER_DEFAULT_STRICT_MODE = False
    
MUSIC_PAUSE_BETWEEN_SONGS = 1  # In seconds

ON_MEMBER_JOIN_DEFAULT_REASON = "Auto role"

AUTOROOM_DEFAULT_SUFFIX = "room"

# S3
S3_CONF_FILE_NAME = 's3.conf.json'
S3_BOt_TOKEN_FILE_NAME = 'bot.token'
BOT_DESCRIPTION = "Hello, i am just a bot, beep boop"