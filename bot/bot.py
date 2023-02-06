import logging
import os
import requests
import json

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get("TG_TOKEN"))
dp = Dispatcher(bot)

HOST_URL = "http://127.0.0.1:8000"


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

    res = json.loads(requests.post(url, data=json.dumps(data)).text)

    await message.reply(f"{res['message']}")


@dp.message_handler(commands=['bye'])
async def stop_bot(message: types.Message):
    url = f"{HOST_URL}/user"

    tg_id = str(message.chat.id)

    data = {"tg_id": tg_id}

    res = json.loads(requests.delete(url, data=json.dumps(data)).text)

    await message.reply(f"{res['message']}")


@dp.message_handler(commands=['mypills'])
async def send_welcome(message: types.Message):
    url = f"{HOST_URL}/pills"
    tg_id = str(message.chat.id)
    data = {"tg_id": tg_id}

    request = requests.get(url, data=json.dumps(data))
    response = json.loads(request.text)

    pills_list = "\n".join(f"• {val}" for _, val in response["message"].items())

    await message.answer(f"Вот список твоих лекарств:\n\n{pills_list}")


@dp.message_handler(commands=['addpill'])
async def send_welcome(message: types.Message):
    url = f"{HOST_URL}/pills"

    await message.reply(f"Напиши название лекарства, о котором я буду тебе напоминать")

    @dp.message_handler()
    async def text(message: types.Message):

        tg_id = str(message.chat.id)

        data = {"tg_id": tg_id, "pill_name": message.text}

        res = json.loads(requests.post(url, data=json.dumps(data)).text)
        print(res)

        await bot.send_message(message.chat.id, f"{res['message']}")


@dp.message_handler(commands=['delpill'])
async def send_welcome(message: types.Message):
    base_url = "http://127.0.0.1:8000/pills/"

    get_list_pills = requests.get(base_url).text
    markup = types.InlineKeyboardMarkup(row_width=2)
    pills_list = json.loads(get_list_pills)

    to_markup = pills_list["pills"]

    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in to_markup.items())
    markup.row(*row_btns)

    await message.reply(f"Выбери название лекарства, о котором я больше не буду тебе напоминать", reply_markup=markup)

    @dp.callback_query_handler()
    async def text(callback: types.CallbackQuery):
        res = requests.delete(f"{base_url}del/{callback.data}")
        del_pill = json.loads(res.text)
        print(callback.message)

        await message.answer(f"{del_pill['message']}" if res.status_code == 200 else f"Ошибка")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
