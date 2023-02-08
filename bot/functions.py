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



