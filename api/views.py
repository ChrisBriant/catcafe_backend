from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.functions import Substr, Lower
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.timezone import make_aware
from rest_framework.decorators import api_view,authentication_classes,permission_classes,action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.tokens import RefreshToken
#from catcafe.permissions import is_authorised
from catcafe.settings import BASE_URL
from .serializers import *
#from difflib import SequenceMatcher
from cats.models import *
from booking.models import *
# from email_validator import validate_email, EmailNotValidError
from password_validator import PasswordValidator
from catcafe.email import sendjoiningconfirmation, sendpasswordresetemail
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random, json, pytz
import pandas as pd



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



@api_view(['POST','OPTIONS'])
def get_token(request):
    if request.method == "POST":
        try:
            email = request.data["email"]
            password = request.data["password"]
            user = authenticate(username=email,password=password)
            if user:
                print('USER',user.__dict__)
                if user.is_enabled:
                    #Issue token
                    token = get_tokens_for_user(user)
                    return Response(token, status=status.HTTP_200_OK)
                else:
                    print("Account Disabled")
                    return Response(ResponseSerializer(GeneralResponse(False,"User is not enabled")).data, status=status.HTTP_400_BAD_REQUEST)
            else:
                print("Credentials Failed")
                return Response(ResponseSerializer(GeneralResponse(False,"User name or password are incorrect")).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(ResponseSerializer(GeneralResponse(False,"Unable to retrieve token")).data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    password = request.data['password']
    passchk = request.data['passchk']
    username = request.data['username']
    email = request.data['email']

    # Create a schema
    schema = PasswordValidator()
    schema\
    .min(8)\
    .max(100)\
    .has().uppercase()\
    .has().lowercase()\
    .has().digits()\
    .has().no().spaces()\

    if password != passchk or not schema.validate(password):
        return Response(ResponseSerializer(GeneralResponse(False,'Password does not meet the complexity requirements.')).data, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = Account.objects.create_user (email,username,password)
        #Get joining confirmation information over to user
        user.hash = hex(random.getrandbits(128))
        user.save()
        url = BASE_URL + "confirm/" + user.hash + "/"
        sendjoiningconfirmation(url,user.name,user.email)
        return Response(ResponseSerializer(GeneralResponse(True,'Account Created')).data, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        print(type(e).__name__)
        return Response(ResponseSerializer(GeneralResponse(False,'Email already exists with us, please try a different one or send a forgot password request')).data, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(ResponseSerializer(GeneralResponse(False,'Problem creating account')).data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgot_password(request):
    email = request.data['email']
    print(email)
    try:
        user = Account.objects.get(email=email)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Email address not found, please register a new account.')).data, status=status.HTTP_400_BAD_REQUEST)
    user.hash = hex(random.getrandbits(128))
    user.save()
    url = BASE_URL + "passwordreset/" + user.hash + "/"
    sendpasswordresetemail(url,user.name,user.email)
    return Response(ResponseSerializer(GeneralResponse(True,'Please check your email and click on the link to reset your password')).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password(request):
    password = request.data['password']
    hash = request.data['hash']
    try:
        user = Account.objects.get(hash=hash)
    except Exception as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Sorry, unable to reset password')).data, status=status.HTTP_400_BAD_REQUEST)
    user.hash = ''
    user.set_password(password)
    user.save()
    return Response(ResponseSerializer(GeneralResponse(True,'Password succesfully changed')).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_cats(request):
    cats = Cat.objects.all()
    serializer = CatSerializer(cats,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_booking(request):
    user = request.user
    date_str = request.data.get('date')
    table_number = request.data.get('table');
    #E.g. "19/06/2021 09:15"
    format = "%d/%m/%Y %H:%M"
    #format = "%Y-%m-%d %H:%M"
    date = datetime.strptime(date_str, format)
    #The date is fixed at the opening times of the cat cafe and assumes local time in the UK
    date_timestamp = datetime.timestamp(pd.Timestamp(date.strftime(format)))
    date_str_start = date.strftime('%m/%d/%Y') + ' 08:30'
    date_str_end = date.strftime('%m/%d/%Y') + ' 20:00'

    date_rng = pd.date_range(start=date_str_start, end=date_str_end, freq='30T')

    if not date.strftime(format) in date_rng.strftime(format).values:
        #Return error 400
        return Response(ResponseSerializer(GeneralResponse(False,'Slot does not exist')).data, status=status.HTTP_400_BAD_REQUEST)

    #Add to the database
    try:
        slot,success = Slot.objects.get_or_create(
            date=make_aware(date),
        )
        table = Table(
            customer = request.user,
            slot=slot,
            table_number = table_number
        )
        table.full_clean()
        table.save()
    except IntegrityError as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Already booked')).data, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response(ResponseSerializer(GeneralResponse(False,'Table does not exist. Must be within range 1-8')).data, status=status.HTTP_400_BAD_REQUEST)

    #Serialize the slots for the day this one is on
    date_from = datetime.combine(date, datetime.min.time())
    delta = timedelta(days=1)
    date_to = date_from + delta
    format = "%Y-%m-%d"
    slots_in_day = Slot.objects.filter(date__range=[make_aware(date_from).strftime(format), make_aware(date_to).strftime(format)]).order_by('date')
    serializer = SlotSerializer(slots_in_day,many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_slots(request):
    date_str = request.query_params['date']
    #Convert to date
    format = "%Y-%m-%d"
    date_from = datetime.strptime(date_str, format)
    delta = timedelta(days=1)
    date_to = date_from + delta
    #Get from DB
    slots_in_day = Slot.objects.filter(date__range=[make_aware(date_from).strftime(format), make_aware(date_to).strftime(format)]).order_by('date')
    serializer = SlotSerializer(slots_in_day,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#Creates a dictionary object containing empty time slots
def create_time_range(start,end,interval):
    times = dict()
    delta = timedelta(minutes=interval)
    date_from = datetime.now().replace(hour=start[0],minute=start[1],second=0,microsecond=0)
    date_to =  datetime.now().replace(hour=end[0],minute=end[1],second=0,microsecond=0) + delta
    while date_from != date_to:
        times[date_from.strftime("%H:%M")] = False
        date_from = date_from + delta
    return times

#Rounds time up in minutes
#https://stackoverflow.com/questions/32723150/rounding-up-to-nearest-30-minutes-in-python/50268328
def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta

def get_available_slots_nuber(day_date,slot_count):
    if day_date == datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) \
        and day_date >= datetime.now().replace(hour=8, minute=30, second=0, microsecond=0):
        #Create datefrome from time now
        date_str_start = ceil_dt(datetime.now(), timedelta(minutes=30)).strftime('%m/%d/%Y %H:%M')
        date_str_end = datetime.now().strftime('%m/%d/%Y') + ' 20:00'
        date_rng = pd.date_range(start=date_str_start, end=date_str_end, freq='30T')
        print("AVAILABLE SLOTS", date_rng)
        return len(date_rng.values)
    else:
        return slot_count


class MonthSlots(object):
    def __init__(self, dictonary):
        self.dict = dictionary

@api_view(['GET'])
def get_month(request):
    #times = create_time_range((8,30),(20,0),30)
    month = request.query_params['month']
    year = request.query_params['year']
    date_from = datetime(day=1,month=int(month),year=int(year))
    #Set the time zone relative to the cat cafe which is either GMT or BST
    cafe_tz = pytz.timezone('Europe/London')
    date_to = date_from +  relativedelta(months=1)
    date_time_today = datetime.now().astimezone(cafe_tz)
    date_today_from_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    format = "%Y-%m-%d"
    slots_in_day = Slot.objects.filter(date__range=[date_from.strftime(format), date_to.strftime(format)]).order_by('date')
    #Remove one date for the panda date frame
    date_to = date_to + timedelta(days=-1)
    #Create a date range, iterate through the days of the month constructing a dictionary with slots
    date_rng = pd.date_range(start=date_from.strftime('%m/%d/%Y'), end=date_to.strftime('%m/%d/%Y'), freq='1D')
    slots_month = dict()
    #Create a list of tubles
    # 0 = date in uk format, 1= time 24hr, 2=date object, 3=table bookings
    slots_date_time = [ (d.date.strftime("%Y-%m-%d"),d.date.strftime("%H:%M"),d.date,d.table_set) for d in slots_in_day]
    for day_of_month in date_rng.strftime(format).values:
        print(datetime.now().astimezone(cafe_tz), datetime.now())
        #Add keys to dict
        day_dict = dict()
        day_dict['times'] = create_time_range((8,30),(20,0),30)
        #Get the times for that day - creates mapping
        slots_for_day = list(filter(lambda x: x[0] == day_of_month, slots_date_time))
        allocated = 0
        for day_slot in slots_for_day:
            #Checks that we are not past the date where the slot is booked
            print(day_slot[3].count())
            #Convert both dates to naive
            time_format = "%Y-%m-%d %H:%M"
            date_1 = datetime.strptime(datetime.strftime(day_slot[2],time_format),time_format)
            date_2 = datetime.strptime(datetime.strftime(date_time_today,time_format),time_format)
            if (date_1>date_2) and day_slot[3].count() == 8:
                print('DATETIME CHECK',date_1,date_2,date_1>date_2)
                allocated += 1
                day_dict['times'][day_slot[1]] = True
        #Check that the day has not passed
        #TODO - Needs to be modified to go more granular if the actual day matches
        #Create method to get the slots that exist for the day
        no_slots = get_available_slots_nuber(datetime.strptime(day_of_month,format),len(day_dict['times']))
        if datetime.strptime(day_of_month,format) >= date_today_from_midnight:
            day_dict['allocated'] = allocated
            day_dict['available'] = no_slots - allocated
        else:
            #There are no available slots all allocated because the day has passed
            day_dict['allocated'] = len(day_dict['times'])
            day_dict['available'] = 0
        slots_month[day_of_month] = day_dict
    return JsonResponse(slots_month)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_slot(request):
    booking_id = request.data['booking_id']
    try:
        table = Table.objects.get(id=booking_id)
    except Exception as e:
        return Response(status=status.HTTP_204_NO_CONTENT)
    #Check authorised
    if (table.customer == request.user) or request.user.is_staff:
        table.delete()
        return Response(ResponseSerializer(GeneralResponse(True,'Successfully deleted booking.')).data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def my_slots(request):
    slots = Slot.objects.filter(customer=request.user)
    serializer = SlotSerializer(slots,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
