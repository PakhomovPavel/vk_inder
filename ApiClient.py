
"""
https://oauth.vk.com/authorize?client_id=вашегоприложения&display=page&scope=stats.offline&response_type=token&v=5.131
"""

from config import user_token
import requests
from pprint import pprint
import datetime
data = datetime.date.today().year



class VkApiClient:
    def __init__(self, user_token: str, api_version: str, base_url: str = "https://api.vk.com/"):
        self.user_token = user_token
        self.api_version = api_version
        self.base_url = base_url

    def general_params(self):
        return {
            "access_token": self.user_token,
            "v": self.api_version,
        }


    def get_info(self, user_ids,):
        params = {
            "user_ids": user_ids,
            "fields": 'bdate, sex, city, relation, is_closed, can_access_closed'

        }
        try:
            return requests.get(f"{self.base_url}/method/users.get",
                                params={**params, **self.general_params()}).json()['response']
        except:
            print("Проверте токен https://oauth.vk.com/authorize?client_id= вставьте id приложения &display=page&scope=stats.offline&response_type=token&v=5.131")





    def name_users(self, user_ids):
        self.name = self.get_info(user_ids)[0]['last_name']
        self.first_name = self.get_info(user_ids)[0]['first_name']
        return f"{self.name} {self.first_name}"


    def bdate_info(self, user_ids):
        bdate = self.get_info(user_ids)[0]['bdate']
        return bdate



    def sex_info(self, user_ids):
        sex = self.get_info(user_ids)[0]['sex']
        return sex

    def city_info(self, user_ids):
        city = self.get_info(user_ids)[0]['city']['title']
        return city

    def relation(self, user_ids):
        relation = self.get_info(user_ids)[0]['relation']
        return relation

    def all_city(self, city):
        params = {
            "q": city,
            "count": 1
        }
        try:
            return requests.get(f"{self.base_url}/method/database.getCities",
                                params={**params, **self.general_params()}).json()['response']['items'][0]['title']
        except IndexError:
            return




    def users_search(self, user_ids, min_age, max_age, city, offset=0):
        if self.get_info(user_ids)[0]['sex'] == 2:
            sex = 1
        else:
            sex = 2
        hometown = city
        offset = offset
        params = {
            "sort": 0,
            "offset": offset,
            "count": 1,
            "hometown": hometown,
            "sex": sex,
            "status": 6,
            "age_from": min_age,
            "age_to": max_age,
            "has_photo": 1,
            "fields": 'city, hometown',
        }

        for profile in requests.get(f"{self.base_url}/method/users.search",
                            params={**params, **self.general_params()}).json()['response']['items']:
            if profile['is_closed'] == False and profile['can_access_closed'] == True:
                profile_id = profile['id']
                name = [profile['first_name'], profile['last_name']]
                return [profile_id, name, self.photo_search(profile_id)]



    def photo_search(self, owner_id):
        params = {
            "owner_id": owner_id,
            "album_id": 'profile',
            "photo_sizes": 0,
            "extended": 'likes, comments'
        }

        popular = []
        result = []
        try:
            for i in requests.get(f"{self.base_url}/method/photos.get",
                                params={**params, **self.general_params()}).json()['response']['items']:
                popular.append(i['comments']['count'] + i['likes']['count'])
                likes = i['comments']['count'] + i['likes']['count']
                url = i['sizes'][-1]['url']
                dict = {likes: url}
                result.append(dict)

            photo = []
            sort_popular = sorted(popular, reverse=True)[0:3]
            for key in sort_popular:
                for values in result:
                    if values.get(key) != None:
                        photo.append(values.get(key))
            return photo
        except:
           pass


vk_client = VkApiClient(user_token=user_token, api_version="5.131")
# pprint(vk_client.get_info(1))
# pprint(vk_client.name_users(362420338))
# pprint(vk_client.users_search(21199458,19,20,'москва', offset=8))
# pprint(vk_client.get_info(230574022))
# print(vk_client.get_info(23556)[0]['city']['title'])
# print(vk_client.city_info(21199458))
# pprint(vk_client.all_city('москва'))
# pprint(datetime.date.today().year)
# pprint(int(vk_client.bdate_info(1)[6:11])-data)
# pprint(vk_client.photo_search(67933))
# 27424