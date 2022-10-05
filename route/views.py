from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from route import models


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    query_filter = {}
    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if location is not None:
        query_filter['location'] = location
    result = models.Route.objects.all().filter(**query_filter)
    print(result)
    return HttpResponse('Ok')


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
    if request.method == 'GET':
        if request.user.has_perm('route.add_event'):
            return render(request, 'add_event_route.html')
        else:
            return HttpResponse('Not allowed to add event')
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        price = request.POST.get('price')
        new_event = models.Event(start_date=start_date, price=price)
        new_event.save()

    return HttpResponse('Info event')


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
