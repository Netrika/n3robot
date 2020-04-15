from n3robot import N3TelegramUser, N3TelegramChat
from telegram import ChatAction
from config import Config
from .manage_chat import register


def send_welcome(update, context):
    """
    Регистрирует событие добавления пользователя в чат.
    Записывает в коллцию telegram_users данные пользователя и добавляет его в список пользователей чата в коллекции telegram_chats
    Если не бот отправляет сообщения 'Hello'.
    :param update:
    :param context:
    :return:
    """

    for member in update.message.new_chat_members:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        if context.bot.id == member.id:
            register(update, context)

        telegram_user = N3TelegramUser(
            id=member.id,
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            is_bot=member.is_bot,
        )
        try:
            telegram_user.save()
        except Exception as e:
            print(f'error - {e}')

        telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
        members = set(telegram_chat.members)
        members.add(telegram_user)
        telegram_chat.members = list(members)
        telegram_chat.save()

        if not member.is_bot:
            text = f'[{member.first_name} {member.last_name}](tg://user?id={member.id}) hello! ' \
                   f'If you\'d like to know what I can you can write /help.'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


def drop_member(update, context):
    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    telegram_user = N3TelegramUser.objects.get(id=update.message.left_chat_member.id)
    telegram_chat.members.remove(telegram_user)
    telegram_chat.save()


def send_gid(update, context):
    """
    Отправляет в чат сообщение с id чата
    :param update:
    :param context:
    :return:
    """
    if 'group' in update.message.chat.type:
        text = update.message.chat_id
    else:
        text = 'This is not a group! Stop fooling me!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def send_url(update, context):
    """
    Парсит сообщение и возвращает ссылку для указания в проекте для получения нотификаций
    :param update:
    :param context:
    :return:
    """

    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    if telegram_chat.api_id:
        sender_url = f'{Config.PROJECT_URL}/gitlab/{telegram_chat.api_id}'
        context.bot.send_message(chat_id=update.effective_chat.id, text=sender_url)


def send_help(update, context):
    """
    Отправляет в чат сообщение с содержимым файла help.j2
    :param update:
    :param context:
    :return:
    """
    with open('templates/bot/help.j2', 'r') as file:
        text = file.read()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')
