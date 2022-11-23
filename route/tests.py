from django.test import TestCase, RequestFactory
from django.test import Client

import route.views
from route.models import Review, Event
from unittest.mock import patch

from route.views import route_add_event, route_reviews


def mockCollection():
    def find_one(self, *args, **kwargs):
        return{}


class mongoClientMock():

    def close(self):
        pass


    def __getitem__(self, item):
        return {'stop_point': mockCollection()}



class TestRoute(TestCase):

    def test_get_review(self):
        client = Client()
        response = client.get('/route/review')

        self.assertEqual(200, response.status_code)


    def test_add_review(self):
        review = Review(
            route_id=2,
            review_text='test',
            review_rate=5
        )
        review.save()
        client = Client()
        response = client.post('/route/review', {'route_id': 1, 'review_text': 'test', 'review_rate': 5})

        self.assertEqual(200, response.status_code)

class TestEvent(TestCase):
    def test_annonimus_user(self):
        client = Client()
        response = client.get('/route/add_event')

        self.assertEqual(401, response.status_code)

        response_client_post = client.post('/route/add_event')
        self.assertEqual(401, response_client_post.status_code)


    def setUp(self):
        self.factory = RequestFactory()

        class userMock():
            def has_perm(self):
                return True
        self.user = userMock
        s

    def test_with_user(self):
        request = self.factory.post('/route/add_event', {'id_route': 1, 'start_date': "2022-06-01", 'price': 399})
        request.user = self.user

        response = route_add_event(request)
        self.assertEqual(response.status_code, 200)
        itms = list(Event.objects.all().filter(price=399))
        self.assertEqual(1, len(itms))
        self.assertEqual(1, itms[0].id_route)


class TestRouteReview(TestCase):
    fixtures = ["reviews.json"]

    def test_with_recieving(self):
        resp = self.client.post('/route/review', {'id_route': 3})
        parsed_resp = resp.json()
        self.assertEqual('ggf', parsed_resp[0]['review_text'])

# Create your tests here.

class RouteInfoTestCase(TestCase):
    fixtures = ["reviews.json"]


    def setUp(self) -> None:
        self.factory = RequestFactory()


    def test_route_info_get(self):
        resp = self.client.get('/rout/info_route')
        self.assertEqual(resp.status_code, 200)

    @patch('utils.mongo_utils.MongoClient', mongoClientMock)
    def test_rote_info_post(self):
        request = self.factory.post('/route/info_route', data={'id_route': 1})

        response = route.views.route_info(request)
