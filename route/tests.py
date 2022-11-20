from django.test import TestCase
from django.test import Client
from route.models import Review
from unittest.mock import patch

from route.views import route_add_event


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

# Create your tests here.
