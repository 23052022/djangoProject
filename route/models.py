import datetime
import json
import os
import django
from django.db import models
from django.utils.translation import gettext_lazy
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

def validate_stopping_point(value):
    try:
        stopping = json.loads(value)
        for itm in stopping:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('ERROR')
    except:
        raise ValidationError('Form is not json')



def validate_route_type(value):
    if value.title() not in ['Car', 'Foot', 'Bike']:
        raise ValidationError('ERROR')

def validate_date(value):
    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
    except:
        raise ValidationError('ERROR')
    if datetime.datetime.today() > parsed_date:
        raise ValidationError('ERROR')


class Places(models.Model):
    name = models.CharField(max_length=50)
    name_country = models.CharField(max_length=50, null=False)


class Route(models.Model):
    starting_point = models.IntegerField()
    stopping_point = models.CharField(max_length=50)
    destination = models.IntegerField()
    country = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.IntegerField()

    class RouteType(models.TextChoices):
        car_ride = 'Car', gettext_lazy('Car')
        on_foot = 'Foot', gettext_lazy('Foot')
        bike_ride = 'Bike', gettext_lazy('Bike')

    route_type = models.CharField(
        max_length=20,
        choices=RouteType.choices,
        default=RouteType.on_foot,
        validators=[validate_route_type]
    )


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=250)
    start_date = models.DateField(validators=[validate_date])
    price = models.IntegerField()
    duration = models.IntegerField()


class Review(models.Model):
    route_id = models.CharField(max_length=50)
    review_text = models.TextField()
    review_rate = models.IntegerField()


