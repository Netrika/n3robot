from telegram import Bot
from datetime import datetime
from fnmatch import fnmatch

from n3robot import N3TelegramChat
from app import huey
from app import app

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
    telegram_chat = N3TelegramChat.objects.get(api_id=api_id)
    if is_mute(telegram_chat):
        return
    project = next((project for project in telegram_chat.projects if project.get('id') == gitlab_project.get('id')), {})
    for project_branch in project.get('branches', []):
        if not fnmatch(branch, project_branch):
            return

    if project:
        n3robot_bot.send_message(
            chat_id=telegram_chat.chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True,
            timeout=60,
            disable_notification=is_silent(telegram_chat)
        )


@huey.task(retries=3, retry_delay=5)
def update_projects_chat(api_id, gitlab_project):
    telegram_chat = N3TelegramChat.objects.get(api_id=api_id)
    for project in telegram_chat.projects:
        if project.get('id') == gitlab_project.get('id'):
            return
    telegram_chat.projects.append(gitlab_project)
    telegram_chat.save()
