import time, logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests
import json
from deep_translator import GoogleTranslator

TOKEN = "6892490196:AAH8Lx5kcdwdii0r6zp9Hd_vRJE8tjpYkL0"
MSG = "Тестовое сообщение! {}"
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
city = ""
api_key = "08bf4c31d4be123471bd36ffd2899f81"


class Form(StatesGroup):
    name = State()


class City:
    name: str
    local_names: object
    lat: float
    lon: float
    country: str
    state: str


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await Form.name.set()
    await message.reply(
        f"Привет, чтобы получить актуальную погоду в выбраном населенном пункте необходимо ввести его название ниже:")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    # Finish our conversation
    await state.finish()
    await message.reply(f"Ищу погоду в населенном пункте: {message.text}")
    user_answer = message.text
    translator = GoogleTranslator().translate(text=message.text)
    await message.reply(translator)
    await get_coords_of_object(translator)


async def get_coords_of_object(name: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={name}&appid={api_key}"
    payload = {}
    proxies = {
        'http': 'http://10.123.123.10:8080',
        'https': '10.123.123.10:8080',
    }
    response = requests.request("GET", url, data=payload, proxies=proxies)

    print(response.text)


if __name__ == "__main__":
    executor.start_polling(dp)
