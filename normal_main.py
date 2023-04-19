from aiogram import *
from aiogram.types import *
import random
import asyncio
import pandas as pd
from json_manager import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from aiogram.utils import exceptions as tg_exceptions

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = 'Токен бота'

df = pd.read_excel('Таблица городов.xlsx')

cities = df[df.columns[0]].tolist()
cities = [w.lower() for w in cities]

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, storage=storage)


class ChatState(StatesGroup):
    user_game_state = State()
    user_game_with_timer_state = State()


# создаю клавиатуру для старта
def start_get_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='О проекте', callback_data="project_info"),
         types.InlineKeyboardButton(text="Правила", callback_data="game_rules"),
         ],
        [types.InlineKeyboardButton(text="Мои очки", callback_data="Мои очки"),
         ],
        [types.InlineKeyboardButton(text="Режимы Игры", callback_data="режимы игры"),
         ],
        [types.InlineKeyboardButton(text='Статистика', callback_data="статистика"),
         ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def game_menu_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Классика", callback_data="начать игру"),
         ],
        [types.InlineKeyboardButton(text="Быстрая игра", callback_data="начать быструю игру"),
         ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def game_statistics_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Общая статистика", callback_data="общая статистика"),
         ],
        [types.InlineKeyboardButton(text="Статистика быстрых игр", callback_data="статистика игр на время"),
         ],
        [types.InlineKeyboardButton(text="Статистика классики", callback_data="статистика обычных игр"),
         ],
        [types.InlineKeyboardButton(text="Лучшие Игроки", callback_data="Лучшие Игроки"),
         ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def all_games_statistics_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Топ город сегодня', callback_data="most_common_city_today_all_games"),
         types.InlineKeyboardButton(text="Топ город все время", callback_data="most_common_city_all_time_all_games"),
         ],
        [types.InlineKeyboardButton(text='Топ буква сегодня', callback_data="most_common_letter_today_all_games"),
         types.InlineKeyboardButton(text="Топ буква все время",
                                    callback_data="most_common_letter_all_time_all_games"),
         ],
        [types.InlineKeyboardButton(text="Лучшие Результаты", callback_data="Лучшие Результаты все игры"),
         ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def fast_game_statistics_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Топ город сегодня', callback_data="most_common_city_today_fast_game"),
         types.InlineKeyboardButton(text="Топ город все время", callback_data="most_common_city_all_time_fast_game"),
         ],
        [types.InlineKeyboardButton(text='Топ буква сегодня', callback_data="most_common_letter_today_fast_game"),
         types.InlineKeyboardButton(text="Топ буква все время",
                                    callback_data="most_common_letter_all_time_fast_game"),
         ],
        [types.InlineKeyboardButton(text="Лучшие Результаты", callback_data="Лучшие Результаты быстрая игра"),
         ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def classic_game_statistics_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Топ город сегодня', callback_data="most_common_city_today_classic_game"),
         types.InlineKeyboardButton(text="Топ город все время", callback_data="most_common_city_all_time_classic_game"),
         ],
        [types.InlineKeyboardButton(text='Топ буква сегодня', callback_data="most_common_letter_today_classic_game"),
         types.InlineKeyboardButton(text="Топ буква все время",
                                    callback_data="most_common_letter_all_time_classic_game"),
         ],
        [types.InlineKeyboardButton(text="Лучшие Результаты", callback_data="Лучшие Результаты класс игра"),
         ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# создаю клавиатуру для города
def city_keyboard(city_name) -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text='Регион', callback_data=f"reg_{city_name}"),
         types.InlineKeyboardButton(text='Население', callback_data=f"nas_{city_name}"),
         ],
        [types.InlineKeyboardButton(text="Федеральный округ", callback_data=f"okr_{city_name}"),
         ],
        [types.InlineKeyboardButton(text='Прежние названия', callback_data=f"pre_{city_name}"),
         ],
        [types.InlineKeyboardButton(text="Год первого упоминания", callback_data=f"god_{city_name}"),
         ],
        [types.InlineKeyboardButton(text="Герб", callback_data=f"ger_{city_name}"),
         ],
        [types.InlineKeyboardButton(text="Завершить игру", callback_data="завершить игру"),
         ],

    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


@dispatcher.message_handler(commands=['start'])
async def send_start_message(message: types.Message = None):
    await message.reply("Привет! Я бот для игры в города. Напиши /menu для попадания в меню")

@dispatcher.message_handler(commands=['menu'])
async def send_welcome(message: types.Message = None):
    global chat_id, user_city, used_cities, game_score, bot_city, user_score
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню! Тут все, что тебе нужно", reply_markup=start_get_keyboard())
    add_user_if_not_exists("users.json", message.from_user.id, '', [1], 0, 0, '', 5,"")
    chat_id = message.from_user.id
    end_game()
    user_city = str(get_user_field('users.json', chat_id, "user_city"))
    used_cities = list(get_user_field('users.json', chat_id, "used_cities"))
    game_score = int(get_user_field('users.json', chat_id, "game_score"))
    user_score = int(get_user_field('users.json', chat_id, "user_score"))
    bot_city = str(get_user_field('users.json', chat_id, "bot_city"))

@dispatcher.callback_query_handler(lambda c: c.data in ['начать игру'])
async def start_goroda_game(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние только для данного пользователя
    await state.set_state(ChatState.user_game_state)
    await bot.send_message(callback_query.from_user.id, "Напишите название города для начала игры")

@dispatcher.callback_query_handler(lambda c: c.data in ['начать быструю игру'])
async def start_goroda_game(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем состояние только для данного пользователя
    await state.set_state(ChatState.user_game_with_timer_state)
    await bot.send_message(callback_query.from_user.id, "Напишите название города для начала игры и подключите все знания в географии)")

# Обработка варианта когда пользователь ничего не написал
@dispatcher.message_handler()
async def unknown_command(message: types.Message):
    await message.reply('Я не знаю такой команды. Используйте /start , чтобы понять, что тут происходит')

def end_game():
    global user_city, used_cities, game_score, bot_city
    update_user_field('users.json', chat_id, "user_city", '')
    update_list_field('users.json', chat_id, "used_cities", [1])
    update_user_field('users.json', chat_id, "game_score", 0)
    update_user_field('users.json', chat_id, "bot_city", '')
    update_user_field('users.json', chat_id, "game_mode", '')

# переаботка chat_id в короткое имя пользователя
async def get_short_name_by_chat_id(chat_id: int, bot: Bot) -> str:
    message: types.Message
    try:
        message = await bot.get_chat(chat_id)
    except tg_exceptions.ChatNotFound:
        return "Chat not found"
    return message.username or message.first_name

def end_game_score_handler(result):
    global game_score
    if result == 'win':
        update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
        update_user_field('users.json', chat_id, "user_score", (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score") + get_user_field('users.json', chat_id, "user_score"))
        add_score_to_json('game_scores.json', (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score"), chat_id)
        game_score = (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score")
    elif result == 'lose':
        update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
        update_user_field('users.json', chat_id, "user_score",
                          ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score")) // 2 + get_user_field('users.json', chat_id, "user_score"))
        add_score_to_json('game_scores.json', ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score")) // 2, chat_id)
        game_score = ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.2 + get_user_field('users.json', chat_id, "game_score")) // 2
    elif result == 'timer_lose':
        update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
        update_user_field('users.json', chat_id, "user_score",
                          ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score")) // 2 + get_user_field('users.json', chat_id, "user_score"))
        add_score_to_json('fast_game_scores.json', ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score")) // 2, chat_id)
        game_score = ((len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score")) // 2
    elif result == 'timer_win':
        update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
        update_user_field('users.json', chat_id, "user_score", (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score") + get_user_field('users.json', chat_id, "user_score"))
        add_score_to_json('fast_game_scores.json', (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score"), chat_id)
        game_score = (len(get_user_field('users.json', chat_id, "used_cities")) - 1) / 2 * 0.8 + get_user_field('users.json', chat_id, "game_score")

@dispatcher.message_handler(state=ChatState.user_game_state)
async def game(message: types.Message, state: FSMContext):
    global user_city, used_cities, game_score, bot_city, user_score, chat_id
    chat_id = message.from_user.id
    update_user_field('users.json', chat_id, "user_city", message.text.strip().lower())
    user_city = get_user_field('users.json', chat_id, "user_city")
    if user_city in cities:
        user_last_letter = user_city[-2] if user_city[-1] in {'ъ', 'ь', 'ы'} else user_city[-1]
        if len(get_user_field('users.json', chat_id, "used_cities")) == 1:
            add_city_to_json('cities.json', user_city, chat_id)
            update_list_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [user_city])
            update_user_field('users.json', chat_id, "bot_city", random.choice([c for c in cities if c.startswith(user_last_letter) and c.lower() not in get_user_field('users.json', chat_id, "used_cities")]))
            bot_city = get_user_field('users.json', chat_id, "bot_city")
            update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [bot_city.lower()])
            await message.reply(bot_city.title(), reply_markup=city_keyboard(bot_city.title()))
            update_user_field('users.json', chat_id, "game_score", 1)
        else:
            bot_last_city = get_user_field('users.json', chat_id, "used_cities")[-1]
            bot_last_letter = bot_last_city[-2] if bot_last_city[-1] in {'ъ', 'ь', 'ы'} else bot_last_city[-1]
            if get_user_field('users.json', chat_id, "user_city") in get_user_field('users.json', chat_id, "used_cities"):
                await message.reply(f"Город {user_city.title()} уже был использован, не ошибайтесь)")
            elif user_city[0] != bot_last_letter:
                await message.reply(
                    f'Название города должно начинаться на букву {bot_last_letter.upper()}, вы потеряли 1 очко :(')
                update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") - 1)
            else:
                update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [user_city])
                add_city_to_json('cities.json', user_city, chat_id)
                possible_for_bot_city = [c for c in cities if
                                         c.startswith(user_last_letter) and c.lower() not in get_user_field('users.json', chat_id, "used_cities")]
                if len(possible_for_bot_city) == 0:
                    end_game_score_handler('win')
                    await bot.send_message(message.from_user.id,
                                           f'Вы выиграли, я не знаю городов на букву {user_last_letter}, получено: {game_score} очков, напишите /menu для новой игры')
                    end_game()
                    await state.finish()
                else:
                    update_user_field('users.json', chat_id, "bot_city", random.choice(possible_for_bot_city))
                    bot_city = get_user_field('users.json', chat_id, "bot_city")
                    update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [bot_city.lower()])
                    await message.reply(bot_city.title(), reply_markup=city_keyboard(bot_city.title()))
                    update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
                    bot_last_letter = bot_city[-2] if bot_city[-1] in {'ъ', 'ь', 'ы'} else bot_city[-1]
                    possible_for_user_cities = [c for c in cities if
                                                c.startswith(bot_last_letter) and c.lower() not in get_user_field(
                                                    'users.json', chat_id, "used_cities")]
                    if len(possible_for_user_cities) == 0:
                        end_game_score_handler('lose')
                        await bot.send_message(message.from_user.id,
                                               f'Вы проиграли, больше нет городов на букву: {bot_last_letter.title()}, получено: {game_score} очков, напишите /menu для новой игры')
                        end_game()
                        await state.finish()
    else:
        await message.reply(f"Подумайте ещё, такого города нет или он очень маленький")


# игровой таймер
async def timer_for_game(state):
    global chat_id
    if get_user_field('users.json', chat_id, "game_mode") == 'fast_game':
        while get_user_field('users.json', chat_id, "user_timer") > 0 and len(get_user_field('users.json', chat_id, "used_cities")) > 1:
            await asyncio.sleep(0.1)
            update_user_field('users.json', chat_id, "user_timer",
                              get_user_field('users.json', chat_id, "user_timer") - 0.1)
        if get_user_field('users.json', chat_id, "user_timer") <= 0 and get_user_field('users.json', chat_id, "game_mode"):
            end_game_score_handler('timer_lose')
            await bot.send_message(chat_id,
                                   f'Время вышло, вы проиграли, получено: {game_score} очков, напишите /menu для новой игры')
            end_game()
            await state.finish()

@dispatcher.message_handler(state=ChatState.user_game_with_timer_state)
async def game_with_timer(message: types.Message, state: FSMContext):
    global user_city, used_cities, game_score, bot_city, user_score, chat_id
    chat_id = message.from_user.id
    update_user_field('users.json', chat_id, "user_city", message.text.strip().lower())
    user_city = get_user_field('users.json', chat_id, "user_city")
    update_user_field('users.json', chat_id, "game_mode", 'fast_game')
    if user_city in cities:
        user_last_letter = user_city[-2] if user_city[-1] in {'ъ', 'ь', 'ы'} else user_city[-1]
        if len(get_user_field('users.json', chat_id, "used_cities")) == 1:
            add_city_to_json('cities_fast.json', user_city, chat_id)
            update_list_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [user_city])
            update_user_field('users.json', chat_id, "bot_city", random.choice([c for c in cities if c.startswith(user_last_letter) and c.lower() not in get_user_field('users.json', chat_id, "used_cities")]))
            bot_city = get_user_field('users.json', chat_id, "bot_city")
            update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [bot_city.lower()])
            await message.reply(bot_city.title())
            update_user_field('users.json', chat_id, "game_score", 1)
            update_user_field('users.json', chat_id, "user_timer", 15)
            await timer_for_game(state)
        else:
            bot_last_city = get_user_field('users.json', chat_id, "used_cities")[-1]
            bot_last_letter = bot_last_city[-2] if bot_last_city[-1] in {'ъ', 'ь', 'ы'} else bot_last_city[-1]
            if get_user_field('users.json', chat_id, "user_city") in get_user_field('users.json', chat_id, "used_cities"):
                await message.reply(f"Город {user_city.title()} уже был использован, не ошибайтесь)")
                update_user_field('users.json', chat_id, "user_timer",
                                  get_user_field('users.json', chat_id, "user_timer") - 5)
            elif user_city[0] != bot_last_letter:
                await message.reply(
                    f'Название города должно начинаться на букву {bot_last_letter.upper()}, вы потеряли 1 очко и 5 секунд :(')
                update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") - 1)
                update_user_field('users.json', chat_id, "user_timer",
                                  get_user_field('users.json', chat_id, "user_timer") - 5)
            else:
                update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [user_city])
                add_city_to_json('cities_fast.json', user_city, chat_id)
                possible_for_bot_city = [c for c in cities if
                                         c.startswith(user_last_letter) and c.lower() not in get_user_field('users.json', chat_id, "used_cities")]
                if len(possible_for_bot_city) == 0:
                    end_game_score_handler('timer_win')
                    await bot.send_message(message.from_user.id,
                                           f'Вы выиграли, я не знаю городов на букву {user_last_letter}, получено: {game_score} очков, напишите /menu для новой игры')
                    end_game()
                    await state.finish()
                else:
                    update_user_field('users.json', chat_id, "bot_city", random.choice(possible_for_bot_city))
                    bot_city = get_user_field('users.json', chat_id, "bot_city")
                    update_user_field('users.json', chat_id, "used_cities", get_user_field('users.json', chat_id, "used_cities") + [bot_city.lower()])
                    await message.reply(bot_city.title())
                    update_user_field('users.json', chat_id, "game_score", get_user_field('users.json', chat_id, "game_score") + 1)
                    bot_last_letter = bot_city[-2] if bot_city[-1] in {'ъ', 'ь', 'ы'} else bot_city[-1]
                    possible_for_user_cities = [c for c in cities if
                                                c.startswith(bot_last_letter) and c.lower() not in get_user_field(
                                                    'users.json', chat_id, "used_cities")]
                    update_user_field('users.json', chat_id, "user_timer", 15)
                    if len(possible_for_user_cities) == 0:
                        end_game_score_handler('timer_lose')
                        await bot.send_message(message.from_user.id,
                                               f'Вы проиграли, больше нет городов на букву:{bot_last_letter.title()}, получено: {game_score} очков, напишите /menu для новой игры')
                        end_game()
                        await state.finish()
    else:
        await message.reply(f"Подумайте ещё, такого города нет или он очень маленький")
        update_user_field('users.json', chat_id, "user_timer",
                          get_user_field('users.json', chat_id, "user_timer") - 5)

# Обработка информации о городе
@dispatcher.callback_query_handler(lambda c: any(c.data.startswith(category) for category in ('reg', 'nas', 'okr', 'pre', 'god', 'ger')) and '_' in c.data, state=ChatState.user_game_state)
async def play_slots_callback(callback_query: types.CallbackQuery):
    row, col = str(callback_query.data), str(callback_query.data)
    index_col = row.find('_')
    index_row = row.find('_') + 1
    city_name = row[index_row:]
    row = row[index_row:]
    col = col[:index_col]
    row = cities.index(row.lower())
    result = df.loc[row, col]
    if col == 'ger':
        await bot.send_photo(callback_query.from_user.id, result, f'Герб города {city_name.title()} ')
    elif col == 'reg':
        await bot.send_message(callback_query.from_user.id, f" Регион города {city_name.title()} : {result} ")
    elif col == 'nas':
        await bot.send_message(callback_query.from_user.id, f" Население города {city_name.title()} : {result} ")
    elif col == 'okr':
        await bot.send_message(callback_query.from_user.id, f" Федеральный округ города {city_name.title()} : {result} ")
    elif col == 'pre':
        await bot.send_message(callback_query.from_user.id, f" Прежние названия города {city_name.title()} : {result} ")
    elif col == 'god':
        await bot.send_message(callback_query.from_user.id, f" Год основания или первого упоминания города {city_name.title()} : {result} ")

@dispatcher.callback_query_handler(lambda c: c.data in ['project_info', 'game_rules', 'Мои очки', "режимы игры", "статистика", "общая статистика", "статистика игр на время", "статистика обычных игр", "Лучшие Игроки"])
async def menus_handler(callback_query: types.CallbackQuery):
    callback_data = str(callback_query.data)
    if callback_data == 'project_info':
        await bot.send_message(callback_query.from_user.id, f"Проект учеников школы 1532. Вся информация о городах взята с сайта: https://www.wikipedia.org. ")
    elif callback_data == 'game_rules':
        await bot.send_message(callback_query.from_user.id, f"В классическом режиме вы называете города и получаете за каждый город, который правильно назвали по 1 очку. Если вы назвали город, который начинается с отличной от последней буквы города бота, то вы теряете 1 очко. При завершении игры или поражении вы получаете очки по формуле: (очки + (кол-во городов названных вами)*0.2)//2. При победе очки зачисляются по формуле: (очки + (кол-во городов названных вами)*0.2). В быстром режиме вы должны называть город в течении 15 секунд и получаете за каждый город, который правильно назвали по 1 очку. Если вы назвали город, который начинается с отличной от последней буквы города бота, то вы теряете 1 очко и 5 секунд времени, данного на размышление.Также вы теряете 5 секунд при использовании уже названного города или несуществующего города. При завершении игры или поражении вы получаете очки по формуле: (очки + (кол-во городов названных вами)*0.8)//2. При победе очки зачисляются по формуле: (очки + (кол-во городов названных вами)*0.8).")
    elif callback_data == 'Мои очки':
        user_score = get_user_field('users.json', chat_id, "user_score")
        await bot.send_message(callback_query.from_user.id, f"Ваши очки: {user_score}")
    elif callback_data == "режимы игры":
        await bot.send_message(callback_query.from_user.id, "Выберете режим игры", reply_markup=game_menu_keyboard())
    elif callback_data == "статистика":
        await bot.send_message(callback_query.from_user.id, "Выберете какую статистику вы хотите просмотреть ", reply_markup=game_statistics_keyboard())
    elif callback_data == "общая статистика":
        await bot.send_message(callback_query.from_user.id, "Выберете, что хотите узнать в общей статистике", reply_markup=all_games_statistics_keyboard())
    elif callback_data == "статистика игр на время":
        await bot.send_message(callback_query.from_user.id, "Выберете, что хотите узнать в статистике быстрых", reply_markup=fast_game_statistics_keyboard())
    elif callback_data == "статистика обычных игр":
        await bot.send_message(callback_query.from_user.id, "Выберете, что хотите узнать в статистике классических игры", reply_markup=classic_game_statistics_keyboard())
    elif callback_data == "Лучшие Игроки":
        lst = top_users('users.json')
        # Сортируем список по убыванию количества элемента
        lst_sort = sorted(lst, key=lambda x: x[1], reverse=True)[:4]
        await bot.send_message(callback_query.from_user.id, f'Топ лучших игроков🏆')
        # Проходим по каждому кортежу в отсортированном списке
        for i, tpl in enumerate(lst_sort):
            if i == 0:
                poz = '🥇'
            elif i == 1:
                poz = '🥈'
            elif i == 2:
                poz = '🥉'
            elif i == 3:
                poz = '💼'
            num = tpl[0]
            count = tpl[1]
            short_name = await get_short_name_by_chat_id(num, bot)
            # Создаем строку вида "количество число"
            result = f" {poz} {count} очков у игрока: @{short_name}"
            await bot.send_message(callback_query.from_user.id, result)


@dispatcher.callback_query_handler(
    lambda c: c.data in ['most_common_city_today_all_games', "most_common_city_all_time_all_games", "most_common_letter_today_all_games", "most_common_letter_all_time_all_games", "Лучшие Результаты все игры"])
async def all_statistic_handler(callback_query: types.CallbackQuery):
    callback_data = str(callback_query.data)
    if callback_data == 'most_common_city_today_all_games':
        city = find_most_common_city_both('today')
        if city == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самый популярный город сегодня: {city.title()}")
    elif callback_data == 'most_common_city_all_time_all_games':
        city = find_most_common_city_both('all_time')
        await bot.send_message(callback_query.from_user.id, f"Самый популярный город за все время: {city.title()}")
    elif callback_data == 'most_common_letter_today_all_games':
        letter = find_most_common_city_letter_both('today')
        if letter == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самая популярная буква сегодня: {letter.title()}")
    elif callback_data == 'most_common_letter_all_time_all_games':
        letter = find_most_common_city_letter_both('all_time')
        await bot.send_message(callback_query.from_user.id, f"Самая популярная буква за все время: {letter.title()}")
    elif callback_data == 'Лучшие Результаты все игры':
        lst = top_game_scores_both()
        await bot.send_message(callback_query.from_user.id, f'Топ лучших результатов🏆')
        # Проходим по каждому кортежу в отсортированном списке
        for i, tpl in enumerate(lst):
            if i == 0:
                poz = '🥇'
            elif i == 1:
                poz = '🥈'
            elif i == 2:
                poz = '🥉'
            elif i == 3:
                poz = '💼'
            num = tpl[1]
            count = tpl[0]
            short_name = await get_short_name_by_chat_id(num, bot)
            # Создаем строку вида "количество число"
            result = f" {poz} {count} очков у игрока: @{short_name}"
            await bot.send_message(callback_query.from_user.id, result)

@dispatcher.callback_query_handler(
    lambda c: c.data in ['most_common_city_today_fast_game', "most_common_city_all_time_fast_game", "most_common_letter_today_fast_game", "most_common_letter_all_time_fast_game", "Лучшие Игроки быстрая игра", "Лучшие Результаты быстрая игра"])
async def all_statistic_handler(callback_query: types.CallbackQuery):
    callback_data = str(callback_query.data)
    if callback_data == 'most_common_city_today_fast_game':
        city = find_most_common_city('cities_fast.json','today')
        if city == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самый популярный город сегодня: {city.title()}")
    elif callback_data == 'most_common_city_all_time_fast_game':
        city = find_most_common_city('cities_fast.json', 'all_time')
        await bot.send_message(callback_query.from_user.id, f"Самый популярный город за все время: {city.title()}")
    elif callback_data == 'most_common_letter_today_fast_game':
        letter = find_most_common_city_letter('cities_fast.json','today')
        if letter == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самая популярная буква сегодня: {letter.title()}")
    elif callback_data == 'most_common_letter_all_time_fast_game':
        letter = find_most_common_city_letter('cities_fast.json', 'all_time')
        await bot.send_message(callback_query.from_user.id, f"Самая популярная буква за все время: {letter.title()}")
    elif callback_data == 'Лучшие Результаты быстрая игра':
        lst = top_game_scores('fast_game_scores.json')
        await bot.send_message(callback_query.from_user.id, f'Топ лучших результатов🏆')
        # Проходим по каждому кортежу в отсортированном списке
        for i, tpl in enumerate(lst):
            if i == 0:
                poz = '🥇'
            elif i == 1:
                poz = '🥈'
            elif i == 2:
                poz = '🥉'
            elif i == 3:
                poz = '💼'
            num = tpl[1]
            count = tpl[0]
            short_name = await get_short_name_by_chat_id(num, bot)
            # Создаем строку вида "количество число"
            result = f" {poz} {count} очков у игрока: @{short_name}"
            await bot.send_message(callback_query.from_user.id, result)

@dispatcher.callback_query_handler(
    lambda c: c.data in ['most_common_city_today_classic_game', "most_common_city_all_time_classic_game", "most_common_letter_today_classic_game", "most_common_letter_all_time_classic_game", "Лучшие Результаты класс игра"])
async def all_statistic_handler(callback_query: types.CallbackQuery):
    callback_data = str(callback_query.data)
    if callback_data == 'most_common_city_today_classic_game':
        city = find_most_common_city("cities.json",'today')
        if city == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самый популярный город сегодня: {city.title()}")
    elif callback_data == 'most_common_city_all_time_classic_game':
        city = find_most_common_city('cities.json','all_time')
        await bot.send_message(callback_query.from_user.id, f"Самый популярный город за все время: {city.title()}")
    elif callback_data == 'most_common_letter_today_classic_game':
        letter = find_most_common_city_letter('cities.json','today')
        if letter == 'Сегодня еще никто не играл':
            await bot.send_message(callback_query.from_user.id, f"Сегодня еще никто не играл")
        else:
            await bot.send_message(callback_query.from_user.id, f"Самая популярная буква сегодня: {letter.title()}")
    elif callback_data == 'most_common_letter_all_time_classic_game':
        letter = find_most_common_city_letter('cities.json','all_time')
        await bot.send_message(callback_query.from_user.id, f"Самая популярная буква за все время: {letter.title()}")
    elif callback_data == 'Лучшие Результаты класс игра':
        lst = top_game_scores('game_scores.json')
        await bot.send_message(callback_query.from_user.id, f'Топ лучших результатов🏆')
        # Проходим по каждому кортежу в отсортированном списке
        for i, tpl in enumerate(lst):
            if i == 0:
                poz = '🥇'
            elif i == 1:
                poz = '🥈'
            elif i == 2:
                poz = '🥉'
            elif i == 3:
                poz = '💼'
            num = tpl[1]
            count = tpl[0]
            short_name = await get_short_name_by_chat_id(num, bot)
            # Создаем строку вида "количество число"
            result = f" {poz} {count} очков у игрока: @{short_name}"
            await bot.send_message(callback_query.from_user.id, result)

@dispatcher.callback_query_handler(lambda c: c.data in ['завершить игру'], state=ChatState.user_game_state)
async def end_game_and_score_callback(callback_query: types.CallbackQuery, state: FSMContext):
    global user_city, used_cities, game_score, user_score
    info = str(callback_query.data)
    if info == 'завершить игру':
        end_game_score_handler('lose')
        await bot.send_message(callback_query.from_user.id, f"Вы завершили игру и получили: {game_score} очков")
        end_game()
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)