#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import connect
import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)

from n3robot.commands import *
from config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


connect(
    db=Config.MONGODB_DATABASE,
    username=Config.MONGODB_USER,
    password=Config.MONGODB_PASSWORD,
    host=Config.MONGODB_HOST,
    authentication_source='admin'
)

updater = Updater(token=Config.TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("register", register))
dp.add_handler(CommandHandler("unregister", unregister))
dp.add_handler(CommandHandler("help", send_help))
dp.add_handler(CommandHandler("getgid", send_gid))
dp.add_handler(CommandHandler("geturl", send_url))

dp.add_handler(silent_conv_handler)
dp.add_handler(mute_conv_handler)
dp.add_handler(conv_handler)

dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, send_welcome))
dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, drop_member))

dp.add_error_handler(error)

updater.start_polling()
updater.idle()
