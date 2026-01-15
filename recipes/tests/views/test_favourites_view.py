from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.tests.helpers import reverse_with_next

class FavouritesViewTest(TestCase):
    """Test suite for the favourites view functions."""
    
    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Test Recipe',
            description='Test description'
        )
    
    def test_favourite_recipe_adds_to_favourites(self):
        self._login_user()
        
        self.assertFalse(self.user.has_favourited(self.recipe))
        
        response = self.client.get(
            reverse('favourite_recipe', kwargs={'recipe_id': self.recipe.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.has_favourited(self.recipe))

    def test_favourite_recipe_when_already_favourited(self):
        self._login_user()
        self.user.favourite_recipe(self.recipe)
        
        response = self.client.get(
            reverse('favourite_recipe', kwargs={'recipe_id': self.recipe.id})
        )
        
        self.assertEqual(response.status_code, 302)
    
    def test_unfavourite_recipe_removes_from_favourites(self):
        self._login_user()
        self.user.favourite_recipe(self.recipe)
        
        response = self.client.get(
            reverse('unfavourite_recipe', kwargs={'recipe_id': self.recipe.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_favourited(self.recipe))

    def test_unfavourite_recipe_when_not_favourited(self):
        self._login_user()
        
        response = self.client.get(
            reverse('unfavourite_recipe', kwargs={'recipe_id': self.recipe.id})
        )
        
        self.assertEqual(response.status_code, 302)
    
    def test_favourite_recipe_requires_authentication(self):
        url = reverse('favourite_recipe', kwargs={'recipe_id': self.recipe.id})
        redirect_url = reverse_with_next('log_in', url)
        
        response = self.client.get(url)
        
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_unfavourite_recipe_requires_authentication(self):
        url = reverse('unfavourite_recipe', kwargs={'recipe_id': self.recipe.id})
        redirect_url = reverse_with_next('log_in', url)
        
        response = self.client.get(url)
        
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_favourites_list_requires_authentication(self):
        url = reverse('favourites_list')
        redirect_url = reverse_with_next('log_in', url)
        
        response = self.client.get(url)
        
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_favourites_list_redirects_to_profile(self):
        self._login_user()
        
        response = self.client.get(reverse('favourites_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("profile_page")}?tab=favourites')
    
    def _login_user(self):
        self.client.login(username=self.user.username, password='Password123')