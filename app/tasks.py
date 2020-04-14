from telegram import Bot
from datetime import datetime
from fnmatch import fnmatch

from n3robot import N3TelegramChat
from app import huey
from app import app
from app import app_logger

n3robot_bot = Bot(token=app.config.get('TELEGRAM_BOT_TOKEN'))


def is_silent(telegram_chat):
    if telegram_chat.silent_until and telegram_chat.silent_until > datetime.now():
        return True
    return False


def is_mute(telegram_chat):
    if telegram_chat.mute_until and telegram_chat.mute_until > datetime.now():
        return True
    return False


@huey.task(retries=3, retry_delay=5)
def send_message(api_id, message, branch, gitlab_project):
    """
    Try to get chat data from DB
    Check mute status
    Get branches for filtering
    If gitlab_project have a branch then looking for a match
    Send message
    :param api_id: uniq ID of chat
    :param message: text message
    :param branch: branch from hook
    :param gitlab_project: summary project from hook
    :return:
    """
    try:
        telegram_chat = N3TelegramChat.objects.get(api_id=api_id)
    except N3TelegramChat.DoesNotExist:
        return

    if is_mute(telegram_chat):
        return


    #TODO remake it!
    is_send = True
    branch_filters = []
    for project in telegram_chat.projects:
        if project.get('id') == gitlab_project.get('id'):
            branch_filters = project.get('branches')
            break

    if branch and branch_filters:
        is_send = False
        for project_branch in branch_filters:
            if fnmatch(branch, project_branch):
                is_send = True
                break

    if is_send:
        response = n3robot_bot.send_message(
            chat_id=telegram_chat.chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            timeout=60,
            disable_notification=is_silent(telegram_chat)
        )
        app_logger.info(response)


@huey.task(retries=3, retry_delay=5)
def update_projects_chat(api_id, gitlab_project):
    try:
        telegram_chat = N3TelegramChat.objects.get(api_id=api_id)
    except N3TelegramChat.DoesNotExist:
        return

    for project in telegram_chat.projects:
        if project.get('id') == gitlab_project.get('id'):
            return

    telegram_chat.projects.append(gitlab_project)
    telegram_chat.save()
