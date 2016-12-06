from django.contrib.auth.models import User, Group
from django.http import Http404
from django.test import TestCase

from accounts.forms import SoundmanCreationForm


class SoundmanAddTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create(username='admin')
        self.admin.set_password("Aadmin123")
        Group.objects.create(name="Administrators").save()
        Group.objects.get(name='Administrators').user_set.add(self.admin)
        self.admin.save()

    # def test_post_request(self):
    #     self.client.force_login(self.admin)
    #     response = self.client.post('/staff/add', {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
    #                                                'username': "smbkzt", "email": "smbekzat@hotmail.com"})
    #     self.assertTrue(response, 200)

    def test_form_is_valid(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': "smbkzt", "email": "smbekzat@hotmail.com"}
        form = SoundmanCreationForm(data=form_data)
        form.save()
        self.assertTrue(form.is_valid())
        User.objects.get(username="smbkzt")

    def test_soundman_exists(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': "admin", "email": "smbekzat@hotmail.com"}
        form = SoundmanCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class StaffPageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.user.set_password("Tester123")
        Group.objects.create(name="Customers").save()
        Group.objects.get(name='Customers').user_set.add(self.user)
        self.user.save()

        self.admin = User.objects.create(username='admin')
        self.admin.set_password("Tester123")
        Group.objects.create(name="Administrators").save()
        Group.objects.get(name='Administrators').user_set.add(self.admin)
        self.admin.save()

    def test_user_get(self):
        get = self.client.get('/staff/')
        self.assertContains(get, 'Авторизация')
        self.assertRaises(Http404)

        # После авторизации
        self.client.force_login(self.admin)
        response = self.client.get('/staff/')
        self.assertTrue(response.status_code, 301)

    # def test_staff_login_post(self):
    #     self.client.force_login(user=self.admin)
    #     response = self.client.get('/staff/')
    #     self.assertContains(response, "Брони")
