import json
from datetime import datetime, date

def add_city_to_json(file_name,name,chat_id):
    # Открываем JSON-файл и загружаем содержимое как список объектов
    with open(str(file_name), 'r+') as file:
        # Попытаться прочитать данные, если они уже существуют
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []

        # Создать новый объект данных
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data = {'city': name, 'datetime': date, 'chat_id': chat_id}

        # Добавить новый объект в массив уже имеющихся данных
        data.append(new_data)

        # Передвинуть указатель в начало файла
        file.seek(0)

        # Записать массив с данными в файл JSON
        json.dump(data, file)

def add_score_to_json(file_name,score,chat_id):
    # Открываем JSON-файл и загружаем содержимое как список объектов
    with open(str(file_name), 'r+') as file:
        # Попытаться прочитать данные, если они уже существуют
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []

        # Создать новый объект данных
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data = {'game_score': score, 'datetime': date, 'chat_id': chat_id}

        # Добавить новый объект в массив уже имеющихся данных
        data.append(new_data)

        # Передвинуть указатель в начало файла
        file.seek(0)

        # Записать массив с данными в файл JSON
        json.dump(data, file)

def find_most_common_city(file_name,period):
    # Прочитать данные из файла JSON.
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Отфильтровать данные в соответствии с переданным параметром
    if period == 'today':
        today = datetime.now().strftime('%Y-%m-%d')
        data = [d for d in data if d['datetime'].startswith(today)]
    elif period == 'all_time':
        pass
    else:
        raise ValueError('Неверный параметр: {}'.format(period))

    # Сгруппировать данные по городам и посчитать количество записей для каждого города
    city_counts = {}
    for d in data:
        city = d['city']
        if city in city_counts:
            city_counts[city] += 1
        else:
            city_counts[city] = 1

    if not data:
        return 'Сегодня еще никто не играл'
    else:
        # Найти самый популярный город
        popular_city = max(city_counts, key=city_counts.get)
        return popular_city

def find_most_common_city_both(period):
    # Прочитать данные из файла JSON.
    with open('cities.json', 'r') as file:
        data_1 = json.load(file)
    with open('cities_fast.json', 'r') as file:
        data_2 = json.load(file)

    # Отфильтровать данные в соответствии с переданным параметром
    if period == 'today':
        today = datetime.now().strftime('%Y-%m-%d')
        data_1 = [d for d in data_1 if d['datetime'].startswith(today)]
        data_2 = [d for d in data_2 if d['datetime'].startswith(today)]
        data = data_1 + data_2
    elif period == 'all_time':
        data = data_1 + data_2
    else:
        raise ValueError('Неверный параметр: {}'.format(period))

    # Сгруппировать данные по городам и посчитать количество записей для каждого города
    city_counts = {}
    for d in data:
        city = d["city"]
        if city in city_counts:
            city_counts[city] += 1
        else:
            city_counts[city] = 1

    if not data:
        return 'Сегодня еще никто не играл'
    else:
        # Найти самый популярный город
        popular_city = max(city_counts, key=city_counts.get)
        return popular_city

def find_most_common_city_letter(file_name,period):
    # Прочитать данные из файла JSON.
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Отфильтровать данные в соответствии с переданным параметром
    if period == 'today':
        today = datetime.now().strftime('%Y-%m-%d')
        data = [d for d in data if d['datetime'].startswith(today)]
    elif period == 'all_time':
        pass
    else:
        raise ValueError('Неверный параметр: {}'.format(period))

    # Сгруппировать данные по городам и посчитать количество записей для каждого города
    city_counts = {}
    first_letter_counts = {}
    for d in data:
        city = d['city']
        if city in city_counts:
            city_counts[city] += 1
        else:
            city_counts[city] = 1
            first_letter = city[0]
            if first_letter in first_letter_counts:
                first_letter_counts[first_letter] += 1
            else:
                first_letter_counts[first_letter] = 1

    if not data:
        return 'Сегодня еще никто не играл'
    else:
        # Найти самую популярную первую букву города
        popular_first_letter = max(first_letter_counts, key=first_letter_counts.get)
        return popular_first_letter

def find_most_common_city_letter_both(period):
    # Прочитать данные из файла JSON.
    with open('cities.json', 'r') as file:
        data_1 = json.load(file)
    with open('cities_fast.json', 'r') as file:
        data_2 = json.load(file)

    # Отфильтровать данные в соответствии с переданным параметром
    if period == 'today':
        today = datetime.now().strftime('%Y-%m-%d')
        data_1 = [d for d in data_1 if d['datetime'].startswith(today)]
        data_2 = [d for d in data_2 if d['datetime'].startswith(today)]
        data = data_1 + data_2
    elif period == 'all_time':
        data = data_1 + data_2
    else:
        raise ValueError('Неверный параметр: {}'.format(period))

    # Сгруппировать данные по городам и посчитать количество записей для каждого города
    city_counts = {}
    first_letter_counts = {}
    for d in data:
        city = d['city']
        if city in city_counts:
            city_counts[city] += 1
        else:
            city_counts[city] = 1
            first_letter = city[0]
            if first_letter in first_letter_counts:
                first_letter_counts[first_letter] += 1
            else:
                first_letter_counts[first_letter] = 1

    if not data:
        return 'Сегодня еще никто не играл'
    else:
        # Найти самую популярную первую букву города
        popular_first_letter = max(first_letter_counts, key=first_letter_counts.get)
        return popular_first_letter

#проверяем есть ли пользователь в файле и если нет, то добавлеяем информацию о нем
def add_user_if_not_exists(users_file, user_id, user_city, used_cities, game_score, user_score,bot_city,user_timer):
    # Читаем данные из файла
    with open(users_file, "r") as f:
        data = json.load(f)

    # Ищем пользователя по ID
    user_found = False
    for user in data["users"]:
        if user["id"] == user_id:
            user_found = True

    # Если пользователя нет, то добавляем его в список

    if not user_found:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_user = {
            "id": user_id,
            "user_city": user_city,
            "used_cities": used_cities,
            "game_score": game_score,
            "user_score": user_score,
            "bot_city": bot_city,
            "reg_date": date,
            "user_timer": user_timer,
        }
        data["users"].append(new_user)

        # Записываем обновленные данные обратно в файл
        with open(users_file, "w") as f:
            json.dump(data, f)

#по id ищем информацию о пользователе и заменяем ее
def update_user_field(users_file, user_id, field_name, field_value):
    # Читаем данные из файла
    with open(users_file, "r") as f:
        data = json.load(f)

    # Изменяем значение поля для пользователя с заданным ID
    for user in data["users"]:
        if user["id"] == user_id:
            user[field_name] = field_value

    # Записываем обновленные данные в файл без выполнения проверки
    with open(users_file, "w") as f:
        json.dump(data, f)

def update_list_field(users_file, user_id, field_name, new_list):
    """
    Заменяет список в файле JSON для пользователя с указанным ID.
    """
    with open(users_file, "r") as f:
        data = json.load(f)

    # Находим пользователя с указанным ID
    for user in data["users"]:
        if user["id"] == user_id:
            # Заменяем список
            user[field_name] = new_list
            # Записываем измененные данные в файл
            with open(users_file, "w") as f:
                json.dump(data, f)


#по id ищем информацию о пользователе и возвращаем ее
def get_user_field(users_file, user_id, field_name):
    # Читаем данные из файла
    with open(users_file, "r") as f:
        data = json.load(f)

    # Ищем пользователя по ID и выводим значение поля
    for user in data["users"]:
        if user["id"] == user_id:
            return user[field_name]

#поиск максимального значения очков у пользователя
def top_users(file_path):
    with open(file_path) as f:
        data = json.load(f)
    users_list = data["users"]
    sorted_users = sorted(users_list, key=lambda user: user["user_score"], reverse=True)
    top_users = sorted_users[:4]  # возьмем топ-3 пользователей по user_score
    top_result = [(user["id"], user["user_score"]) for user in top_users]
    return top_result


def top_game_scores(file_path):
    # 1. Считываем данные из файла в список
    with open(file_path, "r") as f:
        data = json.load(f)

    # 2. Сортируем список по значению game_score в порядке убывания
    data_sorted = sorted(data, key=lambda x: x["game_score"], reverse=True)

    # 3. Выводим первые 3 элемента списка, содержащие тройки game_score и chat_id
    top_scores = []
    for item in data_sorted[:4]:
        chat_id = item['chat_id']
        score = item['game_score']
        top_scores.append((score, chat_id))

    return top_scores

def top_game_scores_both():
    # 1. Считываем данные из файла в список
    with open('game_scores.json', "r") as f:
        data_1 = json.load(f)
    with open('fast_game_scores.json', "r") as f:
        data_2 = json.load(f)
    data = data_1 + data_2
    # 2. Сортируем список по значению game_score в порядке убывания
    data_sorted = sorted(data, key=lambda x: x["game_score"], reverse=True)

    # 3. Выводим первые 3 элемента списка, содержащие тройки game_score и chat_id
    top_scores = []
    for item in data_sorted[:4]:
        chat_id = item['chat_id']
        score = item['game_score']
        top_scores.append((score, chat_id))

    return top_scores




