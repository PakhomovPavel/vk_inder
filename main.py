from ApiClient import data
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token
session_vk = vk_api.VkApi(token=group_token)
from ApiClient import vk_client

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from BD import create_tables, User_bot, Search_result
DSN = 'postgresql://vk_inder_admin:1234@localhost:5432/vk_inder'
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
session_bd = Session()


def listen():
    try:
        for event in VkLongPoll(session_vk).listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    user_id = event.user_id
                    return main(request, user_id)
    except:
        listen()

def last_listen():
    for event in VkLongPoll(session_vk).listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                return request, user_id

def send_msg(user_id, message):
    session_vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})

def send_msg_photo(user_id, message, attachment):
    session_vk.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment, 'random_id': 0})

def main(request, user_id):
    send_msg(user_id, f"Привет {vk_client.name_users(user_id)}\n"
                      f" вот что я могу:\n"
                      f"Чтобы начать поиск напиши мне: 'поиск'\n"
                      f"Что бы выйти из любого меню напиши мне: 'стоп'")
    for request in last_listen():
        if request == "поиск":
            start(user_id)
        if request == "стоп":
            return send_msg(user_id, f"Пока {vk_client.name_users(user_id)}")
        else:
            return main(request, user_id)

def start(user_id):
    if vk_client.city_info(user_id) != None:
        send_msg(user_id, f"ваш город {vk_client.city_info(user_id)} 'да,нет'?")
        for request in last_listen():
            if request == "да":
                return search_age(user_id, city=vk_client.city_info(user_id))
            elif request == "нет":
                send_msg(user_id, "введите город в котором будем искать")
                return definition_city(user_id)
    else:
        return definition_city(user_id)

def definition_city(user_id):
    for request in last_listen():
        city = request
        if vk_client.all_city(city) == None:
            send_msg(user_id, f"город с таким названием не найден, попробуй еще раз!")
            return definition_city(user_id)
        else:
            send_msg(user_id, f"выбран город: {vk_client.all_city(city)}")
            return search_age(user_id, city=vk_client.all_city(city))

def search_age(user_id, city):
    age_user = vk_client.bdate_info(user_id)
    if age_user == 'неудалось определить возраст':
        return search_age_min(user_id, city)
    else:
        age_user = int(age_user[6:])
        min_age = data - age_user - 3
        max_age = data - age_user + 3
        return search(user_id, min_age, max_age, city, offset=0)

def search_age_min(user_id, city):
    send_msg(user_id, f"Укажите минимальный возраст поиска, но не меньше 18 лет")
    for request in last_listen():
        try:
            request = int(request)
            if request < 18:
                send_msg(user_id, f"возраст не должен быть меньше 18 лет, попробуйте еще раз!")
                return search_age_min(user_id, city)
            elif request > 99:
                send_msg(user_id, f"возраст должен быть не больше 99 лет, попробуйте еще раз!")
                return search_age_min(user_id, city)
            else:
                min_age = request
                return search_age_max(user_id, min_age, city)
        except ValueError:
            send_msg(user_id, f"возраст должен содержать только цифры")
            return search_age_min(user_id, city)

def search_age_max(user_id, min_age, city):
    send_msg(user_id, f"Укажите максимальный возраст поиска, но не больше 99 лет")
    for request in last_listen():
        try:
            request = int(request)
            if request > 99:
                send_msg(user_id, f"возраст должен быть не больше 99 лет, попробуй еще раз!")
                return search_age_max(user_id, min_age, city)
            elif request < 18:
                send_msg(user_id, f"возраст не может быть меньше 18 лет, попробуй еще раз!")
                return search_age_max(user_id, min_age, city)
            elif request < min_age:
                send_msg(user_id, f"максимальный возраст не должен быть меньше чем минимальный, попробуй еще раз!")
                return search_age_min(user_id, city)
            else:
                max_age = request
                return search(user_id, min_age, max_age, city, offset=0)
        except ValueError:
            send_msg(user_id, f"возраст должен содержать только цифры")
            return search_age_max(user_id, min_age, city)

def search(user_id, min_age, max_age, city, offset):
    candidat = vk_client.users_search(user_id, min_age, max_age, city, offset=offset)
    send_search(user_id, min_age, max_age, city, offset, candidat)

def send_search(user_id, min_age, max_age, city, offset, candidat):
    resl_id = []
    use_id = []
    for cand_res in session_bd.query(Search_result.id, Search_result.user_bot_id).all():
        resl_id.append(cand_res[0])
        use_id.append(cand_res[1])

    for element in candidat:
        candidat_id = element[0]
        candidat_name = f"{element[1][-1]} {element[1][0]}"
        candidat_photo = element[2]
        quantity_photo = len(candidat_photo)
        if quantity_photo == 3:
            attachment = f"{candidat_photo[0]},{candidat_photo[1]},{candidat_photo[2]}"
        elif quantity_photo == 2:
            attachment = f"{candidat_photo[0]},{candidat_photo[1]}"
        elif quantity_photo == 1:
            attachment = f"{candidat_photo[0]}"
        else:
            attachment = "нет фото"

        if (candidat_id in resl_id and user_id in use_id) == True:
            continue
        else:
            BD_commit(user_id, candidat_id, candidat_name)
            send_msg_photo(user_id, f"https://vk.com/id{candidat_id}\n{candidat_name}\nЧто бы перейти к следующей анкете напиши 'да', что бы вернуться в меню напиши 'нет", attachment)
            for request in last_listen():
                if request == 'да' or request == user_id:
                    continue
                elif request == 'нет' or request == user_id:
                    return
                else:
                    send_msg(user_id, f"Попробуй еще раз! 'да, нет'")
                    last_listen()

    search(user_id, min_age, max_age, city, offset=offset+1)

def BD_commit(user_id, candidat_id, candidat_name):
    bd_user = User_bot(id=user_id, name=vk_client.name_users(user_id))
    try:
        session_bd.add(bd_user)
        session_bd.commit()
    except:
        session_bd.rollback()

    bd_result = Search_result(id=candidat_id, name=candidat_name, user_bot_id=bd_user.id)
    with session_bd.begin():
        session_bd.add(bd_result)
        session_bd.commit()

listen()
# print(search(21199458,20,23,'Москва',0))