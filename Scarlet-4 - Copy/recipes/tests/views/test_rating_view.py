from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from recipes.models import User, Recipe, Rating 

class RatingViewTestCase(TestCase):
    """ Tests of the rating view. """

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            author=self.user, 
            recipe_name='Test Recipe', 
            difficulty=3,
            description='Test description',
            instructions='Step 1\nStep 2'
        )
        self.url = reverse('rate_recipe', kwargs={'pk': self.recipe.id})

    def test_rate_recipe_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/rate/')

    def test_rate_recipe_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse(settings.LOGIN_URL) + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_rate_recipe_disallows_get(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_logged_in_user_can_submit_rating(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, {'rating': 4})

        self.assertRedirects(
            response, 
            reverse('recipe', kwargs={'recipe_id': self.recipe.id})
        )

        self.assertTrue(
            Rating.objects.filter(
                user=self.user,
                recipe=self.recipe,
                rating=4 
            ).exists()
        )
    
    def test_logged_in_user_can_update_rating(self):
        Rating.objects.create(
            user=self.user,
            recipe=self.recipe, 
            rating=2
        )
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, {'rating': 5})

        rating =Rating.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.rating, 5)
    
    def test_invalid_rating_does_not_save(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, {'rating': 10})

        self.assertRedirects(
            response, 
            reverse('recipe', kwargs={'recipe_id': self.recipe.id})
        )

        self.assertFalse(
            Rating.objects.filter(
                user=self.user,
                recipe=self.recipe,
            ).exists()
        )
    