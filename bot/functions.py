from aiogram import types


def create_markup(parse_data):

    markup = types.InlineKeyboardMarkup(row_width=2)
    tmp = list()

    for pos, (idx, name) in enumerate(parse_data.items()):
        tmp.append(types.InlineKeyboardButton(name, callback_data=idx))
        if pos % 2 or pos == len(parse_data) - 1:
            markup.row(*tmp)
            tmp = []

    return markup


def create_markup_pill(parse_data):

    markup = types.InlineKeyboardMarkup(row_width=2)
    tmp = list()

    for pos, pill in enumerate(parse_data):
        tmp.append(types.InlineKeyboardButton(pill["name"], callback_data=pill["id"]))
        if pos % 2 or pos == len(parse_data) - 1:
            markup.row(*tmp)
            tmp = []

    return markup
