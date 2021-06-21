from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from django.db.models import Count, Avg
from accounts.models import Account
from cats.models import *
from django.conf import settings

class GeneralResponse(object):
    def __init__(self, success, message):
        self.success = success
        self.message = message

class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=100)


#Restrict publicly viewable user attributes
class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id','name')


class CatSerializer(serializers.ModelSerializer):
    cat_picture = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ('id','name','age','food','toy','color','breed','cat_picture')

    def get_cat_picture(self,obj):
        try:
            return "{0}{1}".format(settings.BASE_URL[:-1], obj.picture.url)
        except Exception as e:
            return None

#
# class TVImageSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = TVImage
#         fields = ('id','picture',)
#
# class TVShowSerializer(serializers.ModelSerializer):
#     user = serializers.SerializerMethodField()
#     tv_image = serializers.SerializerMethodField()
#     smashup_count = serializers.SerializerMethodField()
#
#
#     class Meta:
#         model = TVShow
#         fields = ('id','name','tv_image','user','smashup_count',)
#
#     def get_tv_image(self,obj):
#         try:
#             image = TVImage.objects.get(show__id=obj.id)
#             return TVImageSerializer(image).data
#         except Exception as e:
#             return None
#
#     def get_user(self,obj):
#         return PublicUserSerializer(obj.user).data
#
#     def get_smashup_count(self,obj):
#         return obj.show1.all().count() + obj.show2.all().count()
#
# #May no longer be required
# class CategorySerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Category
#         fields = ('id','category')
#
# class CategorySmashupSerializer(serializers.ModelSerializer):
#     category = serializers.ReadOnlyField(source='category.category')
#     show_1_average_rating = serializers.SerializerMethodField()
#     show_2_average_rating = serializers.SerializerMethodField()
#     rating_count = serializers.SerializerMethodField()
#     already_rated = serializers.SerializerMethodField()
#         ## TODO: factor in context if user is logged in find if category ratied
#
#     class Meta:
#         model = CategorySmashup
#         fields = ('id','category','show_1_average_rating','show_2_average_rating','rating_count','already_rated')
#
#     def get_show_1_average_rating(self, obj):
#         return obj.categoryscore_set.aggregate(Avg('show_1_rating__rating'))
#
#     def get_show_2_average_rating(self, obj):
#         return obj.categoryscore_set.aggregate(Avg('show_2_rating__rating'))
#
#     def get_rating_count(self,obj):
#         return obj.categoryscore_set.count()
#
#     def get_already_rated(self,obj):
#         if not self.context['user_id']:
#             print('No user')
#             return False
#         else:
#             #Determine if the user ID is in the ratings
#             print('Is user', self.context['user_id'])
#             ratings = obj.categoryscore_set.all().values();
#             ratings_filtered = [r['user_id'] for r in ratings if r['user_id']]
#             if self.context['user_id'] in ratings_filtered:
#                 return True
#             else:
#                 return False
#
# class TVSmashupSerializer(serializers.ModelSerializer):
#     creator = serializers.SerializerMethodField()
#     show1 = serializers.SerializerMethodField()
#     show2 = serializers.SerializerMethodField()
#     categories = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SmashUp
#         fields = ('id','show1','show2','creator','categories')
#
#     def get_show1(self,obj):
#         return TVShowSerializer(obj.show_1).data
#
#     def get_show2(self,obj):
#         return TVShowSerializer(obj.show_2).data
#
#     def get_creator(self,obj):
#         return PublicUserSerializer(obj.creator).data
#
#     def get_categories(self,obj):
#         if not self.context:
#             return CategorySmashupSerializer(obj.categorysmashup_set,many=True,context={'user_id':None}).data
#         else:
#             return CategorySmashupSerializer(obj.categorysmashup_set,many=True,context=self.context).data
#
# class ShowRatingSerializer(serializers.ModelSerializer):
#     show_id = serializers.ReadOnlyField(source='show.id')
#     show_name = serializers.ReadOnlyField(source='show.name')
#
#     class Meta:
#         model = ShowRating
#         fields = ('show_id', 'show_name', 'rating')
#
# class RatingSerializer(serializers.ModelSerializer):
#     category = serializers.SerializerMethodField()
#     show_1_rating = ShowRatingSerializer()
#     show_2_rating = ShowRatingSerializer()
#
#     class Meta:
#         model = CategoryScore
#         fields = ('id','show_1_rating','show_2_rating','category')
#
#     def get_category(self,obj):
#         return CategorySmashupSerializer(obj.categorysmashup,context=self.context).data
#
#
# class ShowsAndSmashupsSerializer(serializers.Serializer):
#     shows = serializers.ListField(child=TVShowSerializer())
#     smashups = serializers.ListField(child=TVSmashupSerializer())
#
# class ShowIndexSerializer(serializers.Serializer):
#     showidx = serializers.CharField()
#     count_shows = serializers.IntegerField()
