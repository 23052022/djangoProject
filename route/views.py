from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from route import models


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")





    filter_string = 'and'.join(query_filter)

    joining = """SELECT  
        route_route.country,
        route_route.destination,
        route_route.duration,
        route_route.stopping_point,
        route_route.route_type,
        start_point.name,
        end_point.name
    
    FROM route_route
    JOIN route_places as start_point
        On start_point.id = route_route.starting_point

        JOIN  route_places as end_point
            ON end_point.id = route_route.destination
WHERE  """ + filter_string

    cursor.execute(joining)

    result = cursor.fetchall()

    new_result = [{'country': i[0], 'description': i[1],
                   'duration': i[2], 'stopping': i[3],
                   'type': i[4], 'start': i[5],
                   'end': i[6]} for i in result]

    return HttpResponse(new_result)


def route_info(request, id):
    result = models.Route.objects.all().filter(id=id)
    return HttpResponse([{'country': itm.country, 'id': itm.id}] for itm in result)


def route_add(request, id):
    if request.method == 'GET':
        return render(request, 'add_route.html')
    if request.method == 'POST':
        dest = request.POST.get('destination')
        start_point = request.POST.get('starting_point')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        route_type = request.POST.get('route_type')

        start_obj = models.Places.objects.get(name=start_point)
        dest_obj = models.Places.objects.get(name=dest)

        new_route = models.Route(location=location, route_type=route_type,
                                 starting_point=start_obj.id, destination=dest_obj.id, country=country,
                                 description=description, duration=duration, stopping_point={}
                                 )
        new_route.save()
    return HttpResponse('Creating a route')


def route_reviews(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    return HttpResponse([{'route_id': itm.route_id, 'review_rate': itm.review_rat}] for itm in result)


def route_add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event_route.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(id_route=route_id,
                                     event_admin=1,
                                     approved_users=[],
                                     pending_users=[],
                                     start_date=start_date, price=price)


            new_event.save()
            return HttpResponse('Adding event')
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


def event_handler(request):
    pass
