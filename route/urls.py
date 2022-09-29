from django.urls import path

from route import views

app_name = 'route'

urlpatterns = [
    path('', views.route_filter, name='index'),
    path('<int:id>', views.route_detail, name='route'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location'),
    path(
        '<int:id>/reviews',
        views.route_reviews, name='route_reviews')
]
