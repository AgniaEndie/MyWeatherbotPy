import http
import time, logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests
import json
from deep_translator import GoogleTranslator, single_detection

TOKEN = "6892490196:AAH8Lx5kcdwdii0r6zp9Hd_vRJE8tjpYkL0"
MSG = "Тестовое сообщение! {}"
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
city = ""
api_key = "08bf4c31d4be123471bd36ffd2899f81"
lang_code = ""


class Form(StatesGroup):
    name = State()
    lang = State()


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
        f"Hello, to get the current weather in a locality you need to enter its name below in your language:")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    # Finish our conversation
    await state.finish()
    global lang_code
    lang_code = single_detection(message.text, api_key="9f2e51bbadd195b968b9c55931009b77")
    answer = GoogleTranslator(target=lang_code).translate(
        text=f"Ищу погоду в населенном пункте: {message.text}")
    await message.reply(answer)
    user_answer = GoogleTranslator(source=lang_code, target=lang_code).translate(text=message.text)
    tr_res = GoogleTranslator().translate(text=message.text)
    tr_res = tr_res.replace(" ", "%20")
    await get_coords_of_object(tr_res, message=message, user_input=user_answer)


async def get_coords_of_object(name: str, message: types.Message, user_input):
    conn = http.client.HTTPSConnection("api.openweathermap.org")
    payload = ''
    headers = {}
    conn.request("GET", f"/data/2.5/weather?q={name}&appid={api_key}", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    weather = data["weather"]
    answer = f"""Погода в городе: {user_input}
        В текущий момент:
        {get_type_of_weather((weather[0])["id"])} {get_emoji_of_weather(weather[0]["id"])} 

        Температура 🌡️:
        В настоящий момент: {round(data['main']['temp'] - 273.15)}
        Ощущается как: {round(data['main']['feels_like'] - 273.15)}
        Максимальная температура сегодня: {round(data["main"]['temp_max'] - 273.15)}
        Минимальная температура сегодня: {round(data["main"]['temp_min'] - 273.15)}
        """
    answer = GoogleTranslator(source="ru", target=lang_code).translate(text=answer)
    await message.reply(answer)


def get_type_of_weather(weather_code):
    if 199 < weather_code < 300:
        return "ThunderStorm"
    elif 299 < weather_code < 500:
        return "Drizzle"
    elif 499 < weather_code < 600:
        return "Rainy"
    elif 599 < weather_code < 700:
        return "Snowy"
    elif 699 < weather_code < 800:
        return "Windy"
    elif weather_code == 800:
        return "Clear weather"
    elif weather_code > 800:
        return "Cloudy"


def get_emoji_of_weather(weather_code):
    if 199 < weather_code < 300:
        return "⛈️"
    elif 299 < weather_code < 500:
        return "🌦️"
    elif 499 < weather_code < 600:
        return "🌧️"
    elif 599 < weather_code < 700:
        return "🌨️"
    elif 699 < weather_code < 800:
        return "🌫️"
    elif weather_code == 800:
        return "☀️/🌕"
    elif weather_code > 800:
        return "☁️"


if __name__ == "__main__":
    executor.start_polling(dp)
