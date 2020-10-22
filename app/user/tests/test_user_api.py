from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPiTests(TestCase):
    """Test the users API(public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_vaild_user_success(self):
        """Test Creating user with valid payload is successful"""
        payload = {
            'email': 'test@londandev.com',
            'password': 'testpass',
            'name': 'test name',
        }

        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)


    def test_user_exists(self):
        """Test if user is already exists fails"""

        payload = {
            'email': 'test@londandev.com',
            'password': 'testpass',
            'name': 'Test',
            }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more that 5 char"""

        payload = {
            'email': 'test@londandev.com',
            'password': 'pw',
            'name': 'Test',
            }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exits = get_user_model().objects.filter(
        email = payload['email']
        ).exists()
        self.assertFalse(user_exits)

    def test_create_token_for_user(self):
        """Test a token is created for user"""
        payload = {
            'email': 'test@londandev.com',
            'password': 'testpass',
            'name': 'Test',
            }

        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)

        self.assertIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_Invaild_Credentails(self):
        """Test a token is not created if invalid cred is given"""


        create_user(email = 'test@londandev.com',password = 'testpass')
        payload = {
            'email': 'test@londandev.com',
            'password': 'wrong',

            }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,  status.HTTP_400_BAD_REQUEST)

    def test_create_token_Without_User(self):
        """Test a token is not created if user doesn't exists"""

        payload = {
            'email': 'test@londandev.com',
            'password': 'wrong',

            }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,  status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test a email or passwrd are reqired"""

        payload = {
            'email': 'test@londandev.com',
            'password': '',

            }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,  status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test auth is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API that requires authentication"""

    def setUp(self):
        self.user = create_user(
        email = 'test@londandev.com',
        password = 'testpass',
        name = 'Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retrive profile for logged in user"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
        'name': self.user.name,
        'email': self.user.email
        })


    def test_post_me_not_allowed(self):
        """Test that post is not allowed on the me url"""
        res = self.client.post(ME_URL,{})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        """Test updating the user profile for auth users"""

        payload = {'name' : 'new_name', 'password': 'newpassword'}

        res = self.client.patch(ME_URL,payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
