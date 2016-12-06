from django.contrib.auth.models import User, Group
from django.test import TestCase


class BookingPageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester', email="bekzat.983@mail.ru")
        self.user.set_password("Tester123")
        Group.objects.create(name="Customers").save()
        Group.objects.get(name='Customers').user_set.add(self.user)
        self.user.save()

        Group.objects.create(name="Soundmans").save()

    def test_redirecting(self):
        response = self.client.post('/accounts/login', {'username': 'tester', 'password': 'Tester123'})
        self.assertRedirects(response, '/')

    def test_booking_post(self):
        self.client.force_login(self.user)
        self.client.get('/step_2/2/')
        response2 = self.client.post('/step_2/2/', {'date': "2016/12/12"})
        self.assertTrue('Расписание звукорежиссера' in response2.content.decode())

    def test_booking_get(self):
        self.client.force_login(self.user)
        response = self.client.get('/step_1')
        self.assertTrue(response.status_code, 200)

    def test_booking_without_logging(self):
        response = self.client.get('/step_1')
        self.assertRedirects(response, '/accounts/login/?next=/step_1')
