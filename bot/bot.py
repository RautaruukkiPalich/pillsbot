import logging
import os
import requests
import json


from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO)

HOST_URL = os.environ.get("HOST_URL")
TOKEN = os.environ.get("TG_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    enter_pill_name = State()


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    url = f"{HOST_URL}/user"

    tg_id = str(message.chat.id)
    name = message.chat.first_name
    surname = message.chat.last_name

    if name is None:
        name = " "

    if surname is None:
        surname = " "

    data = {"tg_id": tg_id,
            "first_name": name,
            "last_name": surname,
            }

    request = requests.post(url, data=json.dumps(data))
    response = json.loads(request.text)

    await message.reply(f"{response['message']}")


@dp.message_handler(commands=['bye'])
async def stop_bot(message: types.Message):
    url = f"{HOST_URL}/user"

    tg_id = str(message.chat.id)

    data = {"tg_id": tg_id}

    request = requests.delete(url, data=json.dumps(data))
    response = json.loads(request.text)

    await message.reply(f"{response['message']}")


@dp.message_handler(commands=['mypills'])
async def my_pills(message: types.Message):
    url = f"{HOST_URL}/pills"
    tg_id = str(message.chat.id)
    data = {"tg_id": tg_id}

    request = requests.get(url, data=json.dumps(data))
    response = json.loads(request.text)

    pills_list = "\n".join(f"• {val}" for _, val in response["message"].items())

    await message.answer(f"Вот список твоих лекарств:\n\n{pills_list}")


@dp.message_handler(commands=['addpill'])
async def add_pill(message: types.Message, state: FSMContext):

    await Form.enter_pill_name.set()
    await message.reply(f"Напиши название лекарства, о котором я буду тебе напоминать.\n\n"
                        f" Для отмены заполнения этого поля можно нажать /cancel")


@dp.message_handler(state=Form.enter_pill_name)
@dp.message_handler(Text(equals='cancel', ignore_case=True), state=Form.enter_pill_name)
async def enter_pill_name(message: types.Message, state: FSMContext):

    url = f"{HOST_URL}/pills"
    data = dict()

    if message.text == "/cancel":
        await bot.send_message(message.chat.id, f"Отменил заполнение поля")
        await state.finish()
        return
    if message.text[0] == "/":
        await bot.send_message(message.chat.id, f"Некорректные данные")
        return

    tg_id = str(message.chat.id)
    data["pill_name"] = str(message.text).title()
    data["tg_id"] = tg_id

    request = requests.post(url, data=json.dumps(data))
    response = json.loads(request.text)

    await state.finish()
    await bot.send_message(message.chat.id, f"{response['message']}")


@dp.message_handler(commands=['delpill'])
async def del_pill(message: types.Message):
    url = f"{HOST_URL}/pills"

    tg_id = str(message.chat.id)
    data = {"tg_id": tg_id}
    text_message = f"Выбери название лекарства, о котором я больше не буду тебе напоминать"

    request = requests.get(url, data=json.dumps(data))
    response = json.loads(request.text)

    markup = types.InlineKeyboardMarkup(row_width=2)

    to_markup = response["message"]

    tmp = list()

    for pos, (idx, name) in enumerate(to_markup.items()):
        tmp.append(types.InlineKeyboardButton(name, callback_data=idx))
        if pos % 2 or pos == len(to_markup) - 1:
            markup.row(*tmp)
            tmp = []

    await message.reply(text_message, reply_markup=markup)

    @dp.callback_query_handler()
    async def text(callback: types.CallbackQuery):
        await callback.message.edit_text(text_message)

        pill_id = str(callback.data)
        data = {"tg_id": tg_id, "pill_id": pill_id}

        request = requests.delete(f"{url}/{pill_id}", data=json.dumps(data))
        response = json.loads(request.text)

        await message.answer(f"{response['message']}" if request.status_code == 200 else f"Ошибка, попробуйте позже")


@dp.message_handler(commands=['end'])
async def end():
    return


#
# @dp.message_handler(content_types="text")
# async def text_handler(message: types.Message):
#     markup = types.ReplyKeyboardRemove()
#     await message.reply(f"Я не умею работать с текстовыми данными. используйте комманды", reply_markup=markup)
#

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
