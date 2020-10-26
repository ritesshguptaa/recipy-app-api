from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def sample_recipe(user, **params):
    """Create and return a sample recipe """
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price' : 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """Test the public avaiabale Recipe api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retriving"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):
    """Test the private available Recipe api """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
        'test1@londandev.com',
        'pass123'
        )


        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retriving tests"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        Serialzer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,Serialzer.data)

    def test_recipe_limited_to_user(self):
        """Test that recipe returned are for the authenticated users"""

        user2 = get_user_model().objects.create_user(
        'other@londandev.com',
        'opass123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        Serialzer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data,Serialzer.data)

    # def test_create_recipe_successful(self):
    #     """Test creating a new recipe"""
    #     payload = {'name':'Cabbage'}
    #     self.client.post(RECIPE_URL, payload)
    #
    #     exists = Recipe.objects.filter(
    #         user = self.user,
    #         name = payload['name'],
    #     ).exists()
    #
    #     self.assertTrue(exists)
    #
    # def test_create_recipe_invalid(self):
    #     """Test creating a new recipe with invalid payload"""
    #     payload = {'name': ''}
    #
    #     res = self.client.post(RECIPE_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
