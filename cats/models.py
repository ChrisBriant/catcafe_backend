from django.db import models
import os, secrets

def image_path_handler(instance, filename):
    fn, ext = os.path.splitext(filename)
    #Create a random filename using hash function
    name = secrets.token_hex(20)
    print("uploading",instance.__dict__)
    return "titleimage_{id}/{name}.png".format(id=instance.id,name=name)


class Cat(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()
    food = models.CharField(max_length=50)
    toy = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    breed = models.CharField(max_length=50)
    picture = models.FileField(upload_to=image_path_handler)
