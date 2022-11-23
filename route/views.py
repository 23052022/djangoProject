
import json
from datetime import datetime
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from route import models
from mongo_utils import MongoDBConnection
from bson import ObjectId
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator




#from pymongo import MongoClient

#client = MongoClient('localhost', 27017)




# Create your views here.
def route_filter(request):
    if request.method =='GET':
        country_list = set()
        country_objs = models.Places.objects.all()
        for itm in range(len(country_objs)):
            country_list.add(country_objs[itm].name_country)
        return render(request, 'route_filter.html', {'country_list': country_list})


    if request.method == 'POST':
        cursor = connection.cursor()
        query_filter = []

        if request.POST.get('route_type') != 'ALL':
            query_filter.append(f"route_type='{request.POST.get('route_type')}'")

        if request.POST.get('country') != 'ALL':
            query_filter.append(f"country='{request.POST.get('country')}'")

        if request.POST.get('location') != '':
            query_filter.append(f"location='{request.POST.get('location')}'")

        if query_filter:
            filter_str = f"WHERE {' and '.join(query_filter)}"
        else:
            filter_str = ""


        sql_query = """SELECT  route_route.country,
                               route_route.description,
                               route_route.duration,
                               route_route.stopping_point,
                               route_route.route_type,
                               start_point.name,
                               end_point.name
    
                    FROM route_route
                        JOIN route_places as start_point
                            ON start_point.id = route_route.starting_point
                        JOIN  route_places as end_point
                            ON end_point.id = route_route.destination"""

        cursor.execute(sql_query + filter_str)
        result_query = cursor.fetchall()

        if result_query:
            list_route = [{'Country': i[0],
                           'Description': i[1],
                           'Duration route': i[2],
                           'Stopping point': i[3],
                           'Route type': i[4],
                           'Start point': i[5],
                           'End': i[6]} for i in result_query]


            p = Paginator(list_route, 2)

            num_page = int(request.GET.get('page', default=1))
            if p.num_pages < num_page:
                num_page = 1
            select_page = p.get_page(num_page)

            return HttpResponse(select_page.object_list)
        else:
            return HttpResponse('Route not found')


def route_info(request):
    if request.method == "GET":
        return render(request, 'info_route.html')

    if request.method == "POST":
        actual_date = datetime.now().strftime('%Y=%m-%d')
        cursor = connection.cursor()

        sql_query_route = f"""SELECT route_route.country,
                                    route_route.description,
                                    route_route.duration,
                                    route_route.stopping_point,
                                    route_route.route_type,
                                    route_route.name,
                                    end_point.name
                              FROM route_route
                                    JOIN route_places as start_point
                                        ON srart_point.id == route_route.starting_point
                                    JOIN route_places as end_point
                                        ON end_point.id == route_route.destination
                                    WHERE route_route.id == '{request.POST,get('id_route')}'"""

        cursor.execute(sql_query_route)
        result_query_route = cursor.fetchall()
        if result_query_route:
            select_route = [{"Country": i[0],
                             "Description": i[1],
                             "Duration": i[2],
                             "Stopping point": i[3],
                             "Route type":[4],
                             "Start point": i[5],
                             "End point": i[6]} for i in result_query_route]

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec =db['stop_points']
                stop_point = collec.find_one({"_id": select_route[0]['Stopping point']})


            sql_query_event = f"""SELECT event.id,
                                         event.start_date,
                                         event.price
                                  FROM route_event as event
                                      JOIN route_route as route 
                                      On route.id == event.id_route
                                  WHERE route.id == '{request.POST.get('id_route')}
                                      and event.start_date >='{actual_date}''"""

            cursor.execute(sql_query_event)
            result_query_route_event = cursor.fetchall()
            if result_query_route_event:
                travel_events = [{'ID Event': i[0],
                                   'Date start event': i[1],
                                   'Price event': i[2]} for i in result_query_route_event]
                return HttpResponse([select_route, travel_events, '<br><a href="info_event" >SELECT EVENT</a>',
                                                                   '<br><a href="add_event" > ADD NEW EVENT</a>'])
            else:
                return HttpResponse([select_route, '<br><a href="add_event" >ADD NEW EVENT</a>'])
        else:
            return HttpResponse('Route not found')



def route_add(request):
    if request.user.has_perm('route.add_route'):
        if request.method == 'GET':
            places_list = []
            country_list = set()
            place_objs = models.Places.objects.all()
            for itm in range(len(place_objs)):
                places_list.append(place_objs[itm].name)
                country_list.add(place_objs[itm].name_country)
            return render(request, 'add_route.html', {'places_list': places_list,
                                                      'country_list': country_list,
                                                      'limit_duratiom': range(1, 11)})

    if request.method == 'POST':
        starting_point = request.POST.get('starting_point')
        destination = request.POST.get('destination')
        stop_points = request.POST.get('stop_points')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        route_type = request.POST.get('route_type')

        models.validate_stopping_point(stop_points)
        stop_list = json.loads(stop_points)

        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collec = db['stop_points']
            id_stop_point = collec.insert_one({'points': stop_list}).inserted_id

        start_obj = models.Places.objects.get(name=starting_point)
        destination_obj = models.Places.objects.get(name=destination)

        new_route = models.Route(starting_point=start_obj.id,
                                 stopping_point=id_stop_point,
                                 destination=destination_obj.id,
                                 country=country,
                                 location=location,
                                 description=description,
                                 duration=duration,
                                 route_type = route_type
                                 )
        new_route.full_clean()
        new_route.save()
        return HttpResponse('Creating a route')
    else:
        return HttpResponse('Not allowed to add route')


def route_reviews(request):
    if request.method == 'GET':
        return render(request, 'route_review.html')

    if request.method == 'POST':
        result = models.Review.objects.all().filter(route_id=request.POST.get('id_route'))
        if result:
            return HttpResponse([{'route_id': i.route_id,
                                  'review_text': i.review_text,
                                  'review_rate': i.review_rate} for i in result])
        else:
            return HttpResponse('Not found reviews', status=404)


def route_add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event_route.html')


        if request.method == 'POST':
            route_id = request.POST.get('id_route')
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(id_route=route_id,
                                     start_date=start_date,
                                     price=price,
                                     event_admin=1
                                     )
            try:
                new_event.full_clean()
                new_event.save()
            except ValidationError:
                return HttpResponse('Date error')

            return HttpResponse('Event added')
    else:

        return HttpResponse('Not allowed to add event')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')

        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=request.form.get('login'), password='secret')
            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('No user')


def user_registration(request):
    if request.method == 'GET':
        return render(request, 'registration')
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST.get('username'),
                                        password=request.POST.get('password'),
                                        email=request.POST.get('email'),
                                        first_name=request.POST.get('first_name'),
                                        last_name=request.POST.get('last_name'))
        user.save()
        return HttpResponse('User is create')
    else:
        return HttpResponse('<a href="logout"> logout</a>')


def logout_user(request):
    logout(request)
    request.user.has_perm('route.event')
    return redirect('/login')


def route_detail(request, id):
    return HttpResponse(f"{id}")


def event_handler(request, event_id):
    cursor = connection.cursor()
    joining = f"""SELECT
    route_event.id_route,
    route_route.country,
    route_route.location,
    route_event.event_admin,
    route_event.approved_users,
    route_event.pending_users,
    route_event.start_date,
    route_event.price,
    route_event.duration

    From route_event
    JOIN route_route
            On route_event.id_route = route_route.id
where route_event.id_route = {event_id}    
    """

    cursor.execute(joining)

    result = cursor.fetchall()
    print(result)
    new_result = [{'id_route': i[0], 'country': i[1], 'location': i[2], 'event_admin': i[3],
                   'approved_users': i[4], 'pending_users': i[5],
                   'start_date': i[6], 'price': i[7],
                   'duration': i[8]} for i in result]

    return HttpResponse(new_result)


def info_event(request):
    pass

def add_me_to_event(rquest):
    pass