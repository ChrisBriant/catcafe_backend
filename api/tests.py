# from rest_framework.test import APIRequestFactory
# from rest_framework.test import APITestCase
# from django.forms.models import model_to_dict
# from tv.models import *
# from accounts.models import *
# from .serializers import *
# import json
#
#
# class TestUpdateCategoriesDetails(APITestCase):
#
#     def create_user(self):
#         user = Account.objects.create_user(
#         	name = "Pob",
# 	        email = "pob@goheart.com",
#         )
#         user.set_password("ILoveTV3!")
#         user.is_enabled = True
#         user.save()
#         return user
#
#     def setup_smashup(self):
#         user = Account.objects.create_user(
#         	name = "Pob",
# 	        email = "pob@goheart.com",
#         )
#         user.set_password("ILoveTV3!")
#         user.is_enabled = True
#         user.save()
#         show1 = TVShow.objects.create(
#             user = user,
#             name = "Pob"
#         )
#         show2 = TVShow.objects.create(
#             user = user,
#             name = 'Teletubbies'
#         )
#         smashup = SmashUp.objects.create(
#             creator = user,
#             show_1 = show1,
#             show_2 = show2
#         )
#         cat1 = Category.objects.create(
#             user = user,
#             category="category 1"
#         )
#         cat2 = Category.objects.create(
#             user = user,
#             category="category 2"
#         )
#         CategorySmashup.objects.create(
#             smashup = smashup,
#             category = cat1
#         )
#         CategorySmashup.objects.create(
#             smashup = smashup,
#             category = cat2
#         )
#         login = {
# 	       "password" : "ILoveTV3!",
# 	       "email" : "pob@goheart.com"
#         }
#         response = self.client.post('/api/authenticate/', json.dumps(login), content_type='application/json')
#         token = response.data['access']
#         self.client.force_authenticate(user=user, token=token)
#         response = self.client.post('/api/getsmashup/?id=1')
#         #print(response.data)
#         #for item in response.data['categories']:
#             #print(item)
#         cat_payload = {
#             'id' : 1,
#             'existing' : [{
#                 'id': 1,
#                 'category': 'category 1',
#                 'average_rating': {'rating__avg': '0'},
#                 'rating_count': 0,
#                 'already_rated' : False
#             }],
#             'new' : [{
#                     'id': 0,
#                     'category': 'new cat 1',
#                     'average_rating': {'rating__avg': '0'},
#                     'rating_count': 0,
#                     'already_rated' : False
#                 },
#                 {
#                     'id': 0,
#                     'category': 'new cat 1',
#                     'average_rating': {'rating__avg': '0'},
#                     'rating_count': 0,
#                     'already_rated' : False
#                 },
#             ],
#         }
#         #print(cat_payload)
#         #Send request
#         response = self.client.post('/api/updatecategories/',json.dumps(cat_payload), content_type='application/json')
#         for item in response.data['categories']:
#             print(item['category'])
