import datetime
import os
import pytz


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
SAVER_DEFAULT_PATH = os.path.join(BASE_PATH, "_Data")
SAVER_DEFAULT_STRICT_MODE = False
    
# COGS

## OnJoin
ON_MEMBER_JOIN_DEFAULT_REASON = "Auto role"

## Autoroom
AUTOROOM_DEFAULT_SUFFIX = "room"
AUTOROOM_EMPTY_LIST_RESPONSE = "Records not found"

## Meme
BASE_MEME_ENDPOINT = 'https://meme-api.com/gimme'
REDDIT_MEME_USER_AGENT = {
    'User-Agent': 'SkomisDiscordBot'
}
REDDIT_SECRET_FILE = 'reddit.conf.json'

GET_REDDIT_CLIENT_ID = lambda: os.getenv('REDDIT_CLIENT_ID')
GET_REDDIT_CLIENT_SECRET = lambda: os.getenv('REDDIT_CLIENT_SECRET')


# DB
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_PATH, "bot.db")}"
TIME_ZONE = pytz.timezone('Europe/Kiev')
GET_TIME_LAMBDA = lambda: datetime.datetime.now(TIME_ZONE)


# S3
S3_CONF_FILE_NAME = 's3.conf.json'
S3_BOt_TOKEN_FILE_NAME = 'bot.token'
BOT_DESCRIPTION = "Hello, i am just a bot, beep boop"
