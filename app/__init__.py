from flask import Flask
from config import Config
from huey import RedisHuey
from mongoengine import connect
from emoji import emojize
import logging

from n3robot import (N3TelegramMessagePipeline, N3TelegramMessagePush, N3TelegramMessageBuild, N3TelegramMessageTagPush)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

app_logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
huey = RedisHuey(host=app.config.get('REDIS_HOST'))

connect(
    db=app.config.get('MONGODB_DATABASE'),
    username=app.config.get('MONGODB_USER'),
    password=app.config.get('MONGODB_PASSWORD'),
    host=app.config.get('MONGODB_HOST'),
    authentication_source='admin'
)

gitlab_hook_map = {
    'Pipeline Hook': N3TelegramMessagePipeline,
    'Push Hook': N3TelegramMessagePush,
    'Job Hook': N3TelegramMessageBuild,
    'Tag Push Hook': N3TelegramMessageTagPush
}

emoji_map = {
    'success_emoji': emojize(':white_check_mark:', use_aliases=True),
    'running_emoji': emojize(':man_running:', use_aliases=True),
    'failed_emoji': emojize(':x:', use_aliases=True),
    'canceled_emoji': emojize(':heavy_minus_sign:', use_aliases=True),
    'skipped_emoji': emojize(':heavy_multiplication_x:', use_aliases=True),
    'commit_emoji': emojize(':pencil:', use_aliases=True),
    'created_emoji': emojize(':bulb:', use_aliases=True),
    'tag_emoji': emojize(':link:', use_aliases=True),
}

from app import routes
