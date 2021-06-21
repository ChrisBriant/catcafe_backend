from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.functions import Substr, Lower
from django.db.utils import IntegrityError
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
from datetime import datetime
import random
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
    #E.g. "19/06/2021 09:15"
    format = "%d/%m/%Y %H:%M"
    #format = "%Y-%m-%d %H:%M"
    date = datetime.strptime(date_str, format)
    date_timestamp = datetime.timestamp(pd.Timestamp(date.strftime(format)))
    date_str_start = date.strftime('%d/%m/%Y') + ' 08:30'
    date_str_end = date.strftime('%d/%m/%Y') + ' 20:00'

    date_rng = pd.date_range(start=date_str_start, end=date_str_end, freq='30T')

    if not date.strftime(format) in date_rng.strftime(format).values:
        #Return error 400
        return Response(ResponseSerializer(GeneralResponse(False,'Slot does not exist')).data, status=status.HTTP_400_BAD_REQUEST)

    #Add to the database
    try:
        Slot.objects.create(
            date=make_aware(date),
            customer = request.user
        )
    except IntegrityError as e:
        print(e)
        return Response(ResponseSerializer(GeneralResponse(False,'Already booked')).data, status=status.HTTP_400_BAD_REQUEST)
    return Response("SPLUNGE", status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_slots(request):
    date_str = request.query_params['date']
    #Convert to date
    format = "%d/%m/%Y %H:%M"
    date = datetime.strptime(date_str, format)
    print(date)
    return Response("McDonalds", status=status.HTTP_201_CREATED)


# # Create your views here.
# @api_view(['POST'])
# @permission_classes([IsAuthenticated,IsAdminUser])
# def new_tvshow(request):
#     # TODO: Look into logic, if no image, etc. do we enforce image upload?
#     name = request.data.get('name')
#     tvshow, success = TVShow.objects.get_or_create(
#         user = request.user,
#         name = name
#     )
#     picture = request.data.get('picture',None)
#     if picture and success:
#         picture = picture
#         try:
#             pic = TVImage(
#                 show = tvshow,
#                 picture=picture
#             )
#             pic.full_clean()
#             pic.save()
#         except Exception as e:
#             print("File upload failed", e)
#             return Response(ResponseSerializer(GeneralResponse(False,"Invalid File")).data, status=status.HTTP_400_BAD_REQUEST)
#     elif picture and not success:
#         #Update picture instead of create new one
#         try:
#             pic = TVImage.objects.get(show_id=tvshow.id)
#             pic.picture = picture
#             pic.full_clean()
#             pic.save()
#         except Exception as e:
#             print("File upload failed", e)
#             return Response(ResponseSerializer(GeneralResponse(False,"Invalid File")).data, status=status.HTTP_400_BAD_REQUEST)
#     serializer = TVShowSerializer(tvshow)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_smashup(request):
#     show1 = request.data.get('show1')
#     show2 = request.data.get('show2')
#     categories = request.data.get('categories')
#     try:
#         show1 = TVShow.objects.get(id=request.data.get('show1'))
#         show2 = TVShow.objects.get(id=request.data.get('show2'))
#     except Exception as e:
#         print(e)
#         return Response(ResponseSerializer(GeneralResponse(False,"At least one of the shows doesn't exist")).data, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         print(request.user, show1,show2)
#         smashup = SmashUp(
#             creator = request.user,
#             show_1 = show1,
#             show_2 = show2
#         )
#         smashup.clean()
#         smashup.save()
#
#         #Create the categories
#         for cat in categories:
#             category, created = Category.objects.get_or_create(
#                 user = request.user,
#                 category = cat
#             )
#             CategorySmashup.objects.create(
#                 smashup = smashup,
#                 category = category
#             )
#         print("here")
#         serializer = TVSmashupSerializer(smashup,context={'user_id' : request.user.id})
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         print(type(e))
#         return Response(ResponseSerializer(GeneralResponse(False,"Unable to create smashup, a smashup probably alredy exists for these shows.")).data, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['GET','POST'])
# def all_smashups(request):
#     smashups = SmashUp.objects.all().order_by('-date_added')
#     serializer = TVSmashupSerializer(smashups,many=True,context={'user_id':request.user.id})
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
#
# @api_view(['GET','POST'])
# def get_smashup(request):
#     try:
#         smashup = SmashUp.objects.get(id=request.query_params['id'])
#     except Exception as e:
#         print(e)
#         return Response(ResponseSerializer(GeneralResponse(False,"Smashup doesn't exist")).data, status=status.HTTP_400_BAD_REQUEST)
#     serializer = TVSmashupSerializer(smashup,context={'user_id':request.user.id})
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def my_smashups(request):
#     smashups = SmashUp.objects.filter(creator=request.user)
#     serializer = TVSmashupSerializer(smashups,many=True)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def my_tvshows(request):
#     shows = TVShow.objects.filter(user=request.user)
#     serializer = TVShowSerializer(shows,many=True)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def search_tvshows(request):
#     searchstr = request.query_params['search']
#     shows = TVShow.objects.filter(name__icontains=searchstr)
#     serializer = TVShowSerializer(shows,many=True)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['GET'])
# def search(request):
#     searchstr = request.query_params['search']
#     shows = TVShow.objects.filter(name__icontains=searchstr)
#     smashups = SmashUp.objects.filter(Q(show_1__name__icontains=searchstr) | Q(show_2__name__icontains=searchstr))
#     showsandsmashups = ShowsAndSmashups(shows,smashups)
#     serializer = ShowsAndSmashupsSerializer(showsandsmashups)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['GET'])
# def shows_first_letter(request):
#     searchstr = request.query_params['letter']
#     shows = TVShow.objects.filter(name__istartswith=searchstr)
#     serializer = TVShowSerializer(shows,many=True)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['GET'])
# def search_id(request):
#     show_id = int(request.query_params['id'])
#     show = TVShow.objects.filter(id=show_id)
#     smashups = SmashUp.objects.filter(Q(show_1__id=show_id) | Q(show_2__id=show_id))
#     showsandsmashups = ShowsAndSmashups(show,smashups)
#     serializer = ShowsAndSmashupsSerializer(showsandsmashups)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def shows_index(request):
#     shows = TVShow.objects.all().annotate(showidx=Lower(Substr('name', 1, 1))) .values('showidx').annotate(count_shows=Count('id')).order_by('showidx')
#     for show in shows:
#         print(show)
#     serializer = ShowIndexSerializer(shows,many=True)
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
# @api_view(['POST'])
# def add_rating(request):
#     catsmashupid = request.data.get('id')
#     show_1 = request.data.get('show_1')
#     show_2 = request.data.get('show_2')
#     categorysmashup = CategorySmashup.objects.get(id=catsmashupid)
#     #Check that the show IDs match
#     if categorysmashup.smashup.show_1.id == show_1['id'] and categorysmashup.smashup.show_2.id == show_2['id']:
#         if request.user.id == None:
#             user = None
#         else:
#             user = request.user
#         if show_1['rating'] in range(1,6) and show_2['rating'] in range(1,6):
#             try:
#                 #Create show rating objects
#                 show_1_rating = ShowRating.objects.create(
#                     show = categorysmashup.smashup.show_1,
#                     rating = show_1['rating']
#                 )
#                 show_2_rating = ShowRating.objects.create(
#                     show = categorysmashup.smashup.show_2,
#                     rating = show_2['rating']
#                 )
#                 rating = CategoryScore.objects.create(
#                     user = user,
#                     show_1_rating = show_1_rating,
#                     show_2_rating = show_2_rating,
#                     categorysmashup = categorysmashup
#                 )
#             except IntegrityError as e:
#                 print(e)
#                 return Response(ResponseSerializer(GeneralResponse(False,"You have already addded a rating for this category.")).data, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 print(e)
#                 return Response(ResponseSerializer(GeneralResponse(False,"Unable to add rating.")).data, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(ResponseSerializer(GeneralResponse(False,"Rating must be a number between 1 and 5")).data, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(ResponseSerializer(GeneralResponse(False,"The shows do not match the smashup")).data, status=status.HTTP_400_BAD_REQUEST)
#     serializer = RatingSerializer(rating,context={'user_id':request.user.id})
#     return Response(serializer.data,status=status.HTTP_200_OK)
#
#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def update_categories(request):
#     try:
#         smashup = SmashUp.objects.get(id=request.data.get('id'),creator=request.user)
#     except Exception as e:
#         return Response(ResponseSerializer(GeneralResponse(False,"You are not authorised to change this Smashup.")).data, status=status.HTTP_401_UNAUTHORIZED)
#     #Get the existing categories extract from DB and then remove ones which are not part of that set
#     existing = request.data.get('existing')
#     print('EXISTING', existing)
#     existing_ids = [e['id'] for e in existing]
#     remove_list = CategorySmashup.objects.exclude(id__in=existing_ids)
#     remove_list.delete()
#     #Add the new categories
#     new_categories = request.data.get('new')
#     new_names = [new['category'] for new in new_categories]
#     for new_cat in new_names:
#         category, created = Category.objects.get_or_create(
#             user = request.user,
#             category = new_cat
#         )
#         CategorySmashup.objects.create(
#             smashup = smashup,
#             category = category
#         )
#     serializer = TVSmashupSerializer(smashup,context={'user_id':request.user.id})
#     return Response(serializer.data,status=status.HTTP_200_OK)
