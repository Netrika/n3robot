from datetime import datetime, timedelta
from jinja2 import Template
import random
import string
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler)
import logging

from n3robot import N3TelegramChat
from config import Config

SILENT = range(1)
MUTE = range(1)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def render_message(api_id, template_name):
    """
    Generates text message from templates.
    :param api_id:
    :param template_name:
    :return: message text
    """
    with open(f'templates/bot/{template_name}') as template_message:
        template = Template(template_message.read())
    return template.render(api_id=api_id, project_url=Config.PROJECT_URL, wiki_url=Config.WIKI_URL)


def register(update, context):
    """
    Creates a document of chat and generates api_id
    :param update:
    :param context:
    :return:
    """

    # from_user = context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=update.message.from_user.id)
    # if from_user.status != 'creator' and from_user.status != 'administrator':
    #     return

    for member in update.message.new_chat_members:
        if context.bot.id != member.id:
            return

    api_id = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
    telegram_chat = N3TelegramChat.objects.filter(chat_id=str(update.effective_chat.id))
    if not telegram_chat:
        telegram_chat = N3TelegramChat(
            chat_id=str(update.effective_chat.id),
            title=str(update.effective_chat.title),
            api_id=str(api_id),
            is_active=True
        )
        try:
            telegram_chat.save()
        except Exception as e:
            logger.error(e)

        text = render_message(api_id=api_id, template_name='register.j2')
        logger.info(f'{telegram_chat.title} created')
        return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')

    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    if not telegram_chat.api_id:
        telegram_chat.update(api_id=api_id)
        telegram_chat.update(is_active=True)
        text = render_message(api_id=api_id, template_name='reregister.j2')
        logger.info(f'{telegram_chat.title} updated')
        return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


def unregister(update, context):
    """
    Меняет статус чата is_active на False.
    Данный атрибут используется для проверки отправки сообщений в чат.
    :param update:
    :param context:
    :return:
    """
    from_user = context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=update.message.from_user.id)
    if from_user.status != 'creator' and from_user.status != 'administrator':
        text = 'Only admins can deactivate chat!'
        return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')

    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    telegram_chat.update(is_active=False)
    telegram_chat.update(api_id=None)
    logger.info(f'{telegram_chat.title} deactivate')
    text = 'Chat deactivate'
    return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


def start_mute(update, context):
    telegram_chat = N3TelegramChat.objects(chat_id=str(update.effective_chat.id))
    if telegram_chat:
        reply_keyboard = [['30', '60', '300'], ['600', '1200', '/cancel']]

        update.message.reply_text(
            'Please, specify the period in minutes',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return MUTE


def set_mute_until(update, context):
    mute_until = datetime.now() + timedelta(minutes=int(update.message.text))
    mute_before_date = mute_until.strftime('%Y-%m-%d %H:%M:%S')

    N3TelegramChat.objects(chat_id=str(update.effective_chat.id)).update(mute_until=mute_until)

    update.message.reply_text(
        f'The mute mode will be active before {mute_before_date}',
        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def start_silent(update, context):
    """
    Запускает диалог с ботом для установки тихого режим.
    Сообщения будут отпралены без уведомления
    :param update:
    :param context:
    :return: возвращает запуск функции set_silent_until
    """
    telegram_chat = N3TelegramChat.objects(chat_id=str(update.effective_chat.id))
    if telegram_chat:
        reply_keyboard = [['30', '60', '300'], ['600', '1200', '/cancel']]

        update.message.reply_text(
            'Please, specify the period in minutes',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return SILENT


def set_silent_until(update, context):
    """
    Прибаавляет к текущему времени количество минут отправленных в чате. Записывает полученное значение в бд.
    :param update:
    :param context:
    :return:
    """
    silent_until = datetime.now() + timedelta(minutes=int(update.message.text))
    silent_before_date = silent_until.strftime('%Y-%m-%d %H:%M:%S')

    N3TelegramChat.objects(chat_id=str(update.effective_chat.id)).update(silent_until=silent_until)

    update.message.reply_text(
        f'The silent mode will be active before {silent_before_date}',
        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def stop_conversation(update, context):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


silent_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('silent', start_silent)],

    states={
        SILENT: [MessageHandler(Filters.regex('^[0-9]+$'), set_silent_until)]
    },

    fallbacks=[CommandHandler('cancel', stop_conversation)]
)

mute_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('mute', start_mute)],

    states={
        MUTE: [MessageHandler(Filters.regex('^[0-9]+$'), set_mute_until)]
    },

    fallbacks=[CommandHandler('cancel', stop_conversation)]
)
