from django.contrib.auth.models import User, Group
from django.test import TestCase

from .forms import UserCreationForm


class LoginTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='tester')
        user.set_password("Tester123")
        Group.objects.create(name="Customers").save()
        Group.objects.get(name='Customers').user_set.add(user)
        user.save()

        admin = User.objects.create(username='administrator')
        admin.set_password("Admin123")
        Group.objects.create(name="Administrators").save()
        Group.objects.get(name='Administrators').user_set.add(admin)
        admin.save()

    def test_login_get(self):
        response = self.client.get('/accounts/login')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Войдите в свой аккаунт' in response.content.decode())

    def test_user_login_post(self):
        response = self.client.post('/accounts/login', {'username': 'tester', 'password': 'Tester123'})
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_admin_login_post(self):
        response = self.client.post('/accounts/login', {'username': 'administrator', 'password': 'Admin123'})
        self.assertEqual(response.status_code, 404)


class RegisterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester', email="bekzat.983@mail.ru")
        self.user.set_password("Tester123")
        Group.objects.create(name="Customers").save()
        Group.objects.get(name='Customers').user_set.add(self.user)
        self.user.save()

    def test_if_username__is_exists(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': 'tester', 'password1': '2251452Bb', 'password2': '2251452Bb',
                     'email': 'bekzat@mail.ru'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_if_email__is_exists(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': 'smbkzt', 'password1': '2251452Bb', 'password2': '2251452Bb',
                     'email': 'bekzat.983@mail.ru'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': 'smbkzt', 'password1': '2251452Bb', 'password2': '2251452Bb',
                     'email': 'bekzat.98@mail.ru'}
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_error_in_form(self):
        form_data = {'first_name': 'Bekzat', 'last_name': 'Shayakhmetov',
                     'username': 'smbkzt', 'password1': '1234566789', 'password2': '123456789',
                     'email': 'bekzat.98@mail.ru'}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_register_get(self):
        response = self.client.get('/accounts/register')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация нового аккаунта')
        self.assertTemplateUsed(response, 'accounts/register.html' and 'bookings/base.html')

    def test_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/accounts/register')
        self.assertContains(response, '404.png')
