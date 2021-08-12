from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from django.db.models import Count, Avg
from accounts.models import Account
from cats.models import *
from booking.models import *
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

class TableSerializer(serializers.ModelSerializer):
    booking_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Table
        fields = ('booking_id','table_number')



class SlotSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    date_str = serializers.SerializerMethodField()
    table_set =  serializers.SerializerMethodField()

    class Meta:
        model = Slot
        fields = ('id','table_set','time','date','date_str','date_booked','date_modified')

    def get_time(self,obj):
        return obj.date.strftime("%H:%M")

    #Helper for front end - friendly format so the date can be naive in JS code
    def get_date_str(self,obj):
        return obj.date.strftime("%Y-%m-%d %H:%M")

    def get_table_set(self,obj):
        return TableSerializer(obj.table_set.order_by('table_number'),many=True).data


class MonthSlotSerializer(serializers.Serializer):
    # intialize fields
    dictionary = serializers.DictField(
    child = serializers.CharField())
