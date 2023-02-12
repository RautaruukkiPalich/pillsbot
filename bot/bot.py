import logging
import requests
import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from constants import TOKEN, HOST_URL, TIME_4ZONE, TIME_SELECT, TIMEZONE
from functions import create_markup, create_markup_pill


bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class CreateUser(StatesGroup):
    callback_timezone = State()


class AddPill(StatesGroup):
    enter_pill_name = State()


class DelPill(StatesGroup):
    callback_pill_id = State()


class EditPillName(StatesGroup):
    callback_pill_id = State()
    enter_pill_name = State()


class EnterScheduleTime(StatesGroup):
    callback_pill_id = State()
    callback_time4zone = State()
    callback_time = State()
    db_query = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled', reply_markup=None)

#
# @dp.message_handler(state='*')
# @dp.message_handler(Text(equals='/', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#     await state.finish()
#     await message.reply('not available', reply_markup=None)


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message, state: FSMContext):
    url = f"{HOST_URL}/user"

    context = dict()
    context["tg_id"] = message.chat.id

    request = requests.get(url, data=json.dumps(context))
    response = json.loads(request.text)

    if response["in_database"] and response["user"]["is_active"]:
        await message.reply(response["text"])
        return

    markup = create_markup(TIMEZONE)
    text_message = f"Выберите ваш часовой пояс"

    async with state.proxy() as memo:
        memo["url"] = url
        memo["message"] = message
        memo["text_message"] = text_message
        memo["context"] = context

    await CreateUser.callback_timezone.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=CreateUser.callback_timezone)
async def start_bot(callback: types.CallbackQuery, state: FSMContext):

    async with state.proxy() as memo:
        url = memo["url"]
        text_message = memo["text_message"]
        message = memo["message"]
        context = memo["context"]

    context["first_name"] = message.chat.first_name
    context["last_name"] = message.chat.last_name
    context["timezone"] = TIMEZONE[int(callback.data)].split()[0]

    request = requests.post(url, data=json.dumps(context))
    response = json.loads(request.text)

    await state.finish()
    await callback.message.edit_text(text_message, reply_markup=None)
    await bot.send_message(message.chat.id, f"{response['text']}")


@dp.message_handler(commands=['bye'])
async def stop_bot(message: types.Message):
    url = f"{HOST_URL}/user"
    context = {"tg_id": message.chat.id}

    request = requests.delete(url, data=json.dumps(context))
    response = json.loads(request.text)

    await message.reply(f"{response['text']}")


@dp.message_handler(commands=['mypills'])
async def my_pills(message: types.Message):
    url = f"{HOST_URL}/pills"
    tg_id = str(message.chat.id)
    context = {"tg_id": tg_id}

    request = requests.get(url, data=json.dumps(context))
    response = json.loads(request.text)

    if not response["in_database"] or not response["user"]["is_active"]:
        await message.answer(response["text"])
        return

    pills_list = "\n".join(
        f"- {pill['name']}" for pill in response["pills"]
    )

    await message.answer(f"Вот список твоих лекарств:\n\n{pills_list}")


@dp.message_handler(commands=['addpill'])
async def add_pill(message: types.Message):
    url = f"{HOST_URL}/user"
    tg_id = str(message.chat.id)
    context = {"tg_id": tg_id}

    request = requests.get(url, data=json.dumps(context))
    response = json.loads(request.text)

    if not response["in_database"] or not response["user"]["is_active"]:
        await message.answer(response["text"])
        return

    await AddPill.enter_pill_name.set()
    await message.reply(f"Напиши название лекарства, о котором я буду тебе напоминать.\n\n"
                        f"Для отмены заполнения этого поля можно нажать /cancel")


@dp.message_handler(state=AddPill.enter_pill_name)
async def enter_pill_name(message: types.Message, state: FSMContext):

    url = f"{HOST_URL}/pills"
    context = dict()

    if message.text[0] == "/":
        await message.reply("Некорректные данные")
        return

    context["pill_name"] = str(message.text)
    context["tg_id"] = str(message.chat.id)

    request = requests.post(url, data=json.dumps(context))
    response = json.loads(request.text)

    await state.finish()
    await message.reply(f"{response['text']}")


@dp.message_handler(commands=['delpill'])
async def del_pill(message: types.Message, state: FSMContext):
    url = f"{HOST_URL}/pills"

    tg_id = str(message.chat.id)
    context = {"tg_id": tg_id}

    request = requests.get(f"{HOST_URL}/user", data=json.dumps(context))
    response = json.loads(request.text)

    if not response["in_database"] or not response["user"]["is_active"]:
        await message.answer(response["text"])
        return

    text_message = f"Выбери название лекарства, о котором я больше не буду тебе напоминать"

    request = requests.get(url, data=json.dumps(context))
    response = json.loads(request.text)

    markup = create_markup_pill(response["pills"])

    async with state.proxy() as memo:
        memo['message'] = message
        memo['text_message'] = text_message
        memo['context'] = context
        memo['url'] = url

    await DelPill.callback_pill_id.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=DelPill)
async def text(callback: types.CallbackQuery, state: FSMContext):

    async with state.proxy() as memo:
        context = memo["context"]
        text_message = memo['text_message']
        url = memo['url']
        message = memo['message']

    await callback.message.edit_text(text_message)

    pill_id = callback.data
    context["pill_id"] = str(pill_id)

    request = requests.delete(f"{url}/{pill_id}", data=json.dumps(context))
    response = json.loads(request.text)

    await state.finish()
    await message.answer(f"{response['text']}" if request.status_code == 200 else f"Ошибка, попробуйте позже")


@dp.message_handler(commands=['editpill'])
async def edit_pill(message: types.Message, state: FSMContext):
    url = f"{HOST_URL}/pills"

    tg_id = str(message.chat.id)
    context = {"tg_id": tg_id}
    text_message = f"Выбери название лекарства, название которого вы хотите изменить"

    request = requests.get(f"{HOST_URL}/user", data=json.dumps(context))
    response = json.loads(request.text)

    if not response["in_database"] or not response["user"]["is_active"]:
        await message.answer(response["text"])
        return

    request = requests.get(url, data=json.dumps(context))
    response = json.loads(request.text)

    markup = create_markup_pill(response["message"])

    async with state.proxy() as memo:
        memo['context'] = context
        memo['url'] = url
        memo['message'] = message
        memo['text_message'] = text_message

    await EditPillName.callback_pill_id.set()
    await message.reply(text_message, reply_markup=markup)


@dp.callback_query_handler(state=EditPillName.callback_pill_id)
async def callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as memo:
        memo['context']['pill_id'] = callback.data
        text_message = memo["text_message"]
        message = memo['message']

    await callback.message.edit_text(text_message)
    await EditPillName.enter_pill_name.set()
    await message.answer(f"Введите новое название\n\n"
                         f"Для отмены заполнения этого поля можно нажать /cancel")


@dp.message_handler(state=EditPillName.enter_pill_name)
async def edit_pill_name(message: types.Message, state: FSMContext):

    if message.text[0] == "/":
        await bot.send_message(message.chat.id, "Некорректные данные")
        return

    async with state.proxy() as memo:
        context = memo["context"]
        url = memo["url"]

    context["pill_name"] = str(message.text)

    request = requests.patch(f"{url}/{context['pill_id']}", data=json.dumps(context))
    response = json.loads(request.text)

    await state.finish()
    await bot.send_message(message.chat.id, f"{response['text']}")


@dp.message_handler(commands=['add_schedule'])
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

    markup = create_markup_pill(response["message"])

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

    tg_id = memo["tg_id"]
    pill_id = memo["pill_id"]
    url_sched = memo["url_sched"]
    choosen_time = TIME_SELECT[time4zone][time_select]

    async with state.proxy() as memo:
        memo["time"] = callback.data

    data = {"tg_id": tg_id, "pill_id": pill_id, "timer": choosen_time}

    request = requests.post(f"{url_sched}", data=json.dumps(data))
    response = json.loads(request.text)

    await state.finish()
    await message.reply(response["message"])


@dp.message_handler(commands=['schedule'])
async def new_schedule(message: types.Message):
    url_sched = f"{HOST_URL}/schedule"

    text_message = f"Твои лекарстава и время их напоминания:\n"

    data = {"tg_id": str(message.chat.id)}

    request = requests.get(url_sched, data=json.dumps(data))
    response = json.loads(request.text)

    if response["in_db"] != "true":
        text_message = f"нет ничего"
        await message.reply(text_message)
        return

    for key, value in response["message"].items():
        text_message += f"\n{'•':>3}{value['name']}\n{', '.join(value['schedules'])}\n"

    await message.reply(text_message)


@dp.message_handler(commands=['end'])
async def end():
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
