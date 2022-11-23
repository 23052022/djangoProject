from django.urls import path

from route import views

app_name = 'route'

urlpatterns = [
    path('', views.route_filter, name='show_filter_route'),
    path('info_route', views.route_info, name='route_info'),
    path('review', views.route_reviews, name='route_reviews'),
    path('add_route>/add_route', views.route_add, name='add_route'),
    path('add_event>', views.route_add_event, name='add_event'),
    path('info_event', views.info_event, name='info_event'),
    path('info_event/<id_event>/add_me', views.add_me_to_event, name='add_me'),

]
