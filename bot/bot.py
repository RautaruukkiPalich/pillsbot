import logging
import requests
import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from constants import TOKEN, HOST_URL, TIME_4ZONE, TIME_SELECT
from functions import create_markup


bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class EnterPillName(StatesGroup):
    enter_pill_name = State()


class EditPillName(StatesGroup):
    callback_pill_id = State()
    enter_pill_name = State()


class EnterScheduleTime(StatesGroup):
    callback_pill_id = State()
    callback_time4zone = State()
    callback_time = State()
    db_query = State()


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

    await EnterPillName.enter_pill_name.set()
    await message.reply(f"Напиши название лекарства, о котором я буду тебе напоминать.\n\n"
                        f" Для отмены заполнения этого поля можно нажать /cancel")


@dp.message_handler(state=EnterPillName.enter_pill_name)
async def enter_pill_name(message: types.Message, state: FSMContext):

    url = f"{HOST_URL}/pills"
    data = dict()

    if message.text[0] == "/":
        if message.text == "/cancel":
            text = f"Отменил заполнение поля"
            await state.finish()
        else:
            text = f"Некорректные данные"
        await bot.send_message(message.chat.id, text)
        return

    tg_id = str(message.chat.id)
    data["pill_name"] = str(message.text)
    data["tg_id"] = tg_id

    request = requests.post(url, data=json.dumps(data))
    response = json.loads(request.text)

    await state.finish()
    await bot.send_message(message.chat.id, f"{response['message']}")


@dp.message_handler(commands=['delpill'])
async def del_pill(message: types.Message, state: FSMContext):
    url = f"{HOST_URL}/pills"

    tg_id = str(message.chat.id)
    data = {"tg_id": tg_id}
    text_message = f"Выбери название лекарства, о котором я больше не буду тебе напоминать"

    request = requests.get(url, data=json.dumps(data))
    response = json.loads(request.text)

    markup = create_markup(response["message"])

    async with state.proxy() as memo:
        memo['message'] = message
        memo['text_message'] = text_message
        memo['tg_id'] = message.chat.id
        memo['url'] = url

    await EnterPillName.enter_pill_name.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EnterPillName)
async def text(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        pass
    text_message = memo['text_message']
    tg_id = memo['tg_id']
    url = memo['url']
    message = memo['message']

    await callback.message.edit_text(text_message)

    pill_id = str(callback.data)
    data = {"tg_id": tg_id, "pill_id": pill_id}

    request = requests.delete(f"{url}/{pill_id}", data=json.dumps(data))
    response = json.loads(request.text)

    await state.finish()
    await message.answer(f"{response['message']}" if request.status_code == 200 else f"Ошибка, попробуйте позже")


@dp.message_handler(commands=['editpill'])
async def edit_pill(message: types.Message, state: FSMContext):
    url = f"{HOST_URL}/pills"

    tg_id = str(message.chat.id)
    data = {"tg_id": tg_id}
    text_message = f"Выбери название лекарства, название которого вы хотите изменить"

    request = requests.get(url, data=json.dumps(data))
    response = json.loads(request.text)

    markup = create_markup(response["message"])

    async with state.proxy() as memo:
        memo['message'] = message
        memo['text_message'] = text_message

    await EditPillName.callback_pill_id.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EditPillName.callback_pill_id)
async def callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        memo['pill_id'] = callback.data

    text_message = memo["text_message"]
    message = memo['message']

    await callback.message.edit_text(text_message)
    await EditPillName.enter_pill_name.set()
    await message.answer(f"Введите новое название\n\n"
                         f"Для отмены заполнения этого поля можно нажать /cancel")


@dp.message_handler(state=EditPillName.enter_pill_name)
async def edit_pill_name(message: types.Message, state: FSMContext):

    url = f"{HOST_URL}/pills"
    data = dict()

    if message.text[0] == "/":
        if message.text == "/cancel":
            text = f"Отменил заполнение поля"
            await state.finish()
        else:
            text = f"Некорректные данные"
        await bot.send_message(message.chat.id, text)
        return

    async with state.proxy() as memo:
        pass

    data["pill_name"] = str(message.text)
    data["pill_id"] = memo["pill_id"]
    data["tg_id"] = str(message.chat.id)

    request = requests.patch(f"{url}/{data['pill_id']}", data=json.dumps(data))
    response = json.loads(request.text)

    text = f"{response['message']}"

    await state.finish()
    await bot.send_message(message.chat.id, text)


@dp.message_handler(commands=['schedule'])
async def new_schedule(message: types.Message, state: FSMContext):
    url_sched = f"{HOST_URL}/schedule"
    url_pill = f"{HOST_URL}/pills"
    text_message = f"Выбери название лекарства, для которого вы хотите назначить время напоминания"

    async with state.proxy() as memo:
        memo["tg_id"] = message.chat.id
        memo["url_sched"] = url_sched
        memo["url_pill"] = url_pill
        memo["message"] = message
        memo["text_message"] = text_message

    data = {"tg_id": memo["tg_id"]}

    request = requests.get(url_pill, data=json.dumps(data))
    response = json.loads(request.text)

    markup = create_markup(response["message"])

    await EnterScheduleTime.callback_time4zone.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EnterScheduleTime.callback_time4zone)
async def new_schedule(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        pass
    text_message = memo["text_message"]
    message = memo["message"]

    await callback.message.edit_text(text_message)

    text_message = "Выберите временной интервал из предложенных"

    async with state.proxy() as memo:
        memo["pill_id"] = callback.data
        memo["text_message"] = text_message

    markup = create_markup(TIME_4ZONE)

    await EnterScheduleTime.callback_time.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EnterScheduleTime.callback_time)
async def new_schedule(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        pass

    text_message = memo["text_message"]
    message = memo["message"]

    await callback.message.edit_text(text_message)

    text_message = "Выберите подходящее время"

    async with state.proxy() as memo:
        memo["time4zone"] = int(callback.data)
        memo["text_message"] = text_message

    markup = create_markup(TIME_SELECT[int(callback.data)])

    await EnterScheduleTime.db_query.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EnterScheduleTime.db_query)
async def new_schedule(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        pass

    text_message = memo["text_message"]
    message = memo["message"]
    time4zone = memo["time4zone"]
    time_select = int(callback.data)

    await callback.message.edit_text(text_message)

    choosen_time = TIME_SELECT[time4zone][time_select]

    text_message = f"Вы выбрали время: {choosen_time}"

    async with state.proxy() as memo:
        memo["time"] = callback.data

    await state.finish()
    await message.reply(text_message, reply_markup=None)


@dp.message_handler(commands=['end'])
async def end():
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
