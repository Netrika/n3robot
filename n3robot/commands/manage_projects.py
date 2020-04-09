#!/usr/bin/env python

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, CallbackQueryHandler, ConversationHandler,
                          MessageHandler, Filters)
from ast import literal_eval

from n3robot import N3TelegramChat

# State definitions for top level conversation
SELECTING_PROJECT, MODIFY_PROJECT, MODIFY_BRANCH = map(chr, range(3))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))

START_OVER, FEATURES, CURRENT_PROJECT, CURRENT_LEVEL = map(chr, range(4))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END


def get_list_projects(update, context):
    """
    Запрашивает список проектов из БД и генерирует из них список кнопок
    :param update:
    :param context:
    :return:
    """
    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    buttons = []
    series = []
    for project in telegram_chat.projects:
        if project:
            project_meta = {'id': project.get("id"), 'name': project.get("name")}
            buttons.append(InlineKeyboardButton(project.get("name"), callback_data=str(project_meta)))
            if len(buttons) == 3:
                series.append(buttons)
                buttons = []
    series.append(buttons)
    keyboard = InlineKeyboardMarkup(series)
    text = 'Choose a project from the list below:'

    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return MODIFY_PROJECT


def stop_projects(update, context):
    text = 'Goodbye!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return END


def get_project_menu(update, context):
    """
    Функция генерирует набор кнопок с настройками проекта
    :param update:
    :param context:
    :return:
    """
    if context.user_data.get(START_OVER):
        project_meta = literal_eval(context.user_data[CURRENT_PROJECT])
    else:
        project_meta = literal_eval(update.callback_query.data)

    buttons = [
        [InlineKeyboardButton('Edit branches', callback_data=str(project_meta))],
        [InlineKeyboardButton('Back', callback_data=str(END))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    text = f'Here it is: {project_meta.get("name")}.\n What do you want to do with the project?'
    if not context.user_data.get(START_OVER):
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return SELECTING_FEATURE


def edit_list_branches(update, context):
    context.user_data[CURRENT_PROJECT] = update.callback_query.data
    update.callback_query.answer()
    text = "OK. Send me a list of branches"
    update.callback_query.edit_message_text(text=text)
    return TYPING


def save_branches(update, context):

    ud = context.user_data
    project_meta = literal_eval(ud[CURRENT_PROJECT])
    telegram_chat = N3TelegramChat.objects.get(chat_id=str(update.effective_chat.id))
    project_obj = next(project for project in telegram_chat.projects if project.get('id') == project_meta.get('id'))

    branches = str(update.message.text).split(' ')
    project_obj.update(branches=branches)
    telegram_chat.save()

    ud[START_OVER] = True
    context.bot.send_message(chat_id=update.effective_chat.id, text='Success! Branches list updated.')
    return get_project_menu(update, context)


def stop_modify_project(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    get_list_projects(update, context)

    return END


settings_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(get_project_menu, pattern='^(?!' + str(END) + ').*$')],

    states={
        SELECTING_FEATURE: [CallbackQueryHandler(edit_list_branches, pattern='^(?!' + str(END) + ').*$')],
        TYPING: [MessageHandler(Filters.text, save_branches)],
    },

    fallbacks=[CallbackQueryHandler(stop_modify_project, pattern='^' + str(END) + '$')],

)

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('projects', get_list_projects)
    ],
    states={
        MODIFY_PROJECT: [settings_conv]
    },
    fallbacks=[
        CallbackQueryHandler(stop_projects, pattern='^' + str(END) + '$'),
        CommandHandler('stop', stop_projects)],
)

conv_handler.states[STOPPING] = conv_handler.entry_points
conv_handler.states[SELECTING_FEATURE] = conv_handler.states[MODIFY_PROJECT]
