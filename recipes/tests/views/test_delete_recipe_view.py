"""Tests for the delete recipe view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.tests.helpers import reverse_with_next


class DeleteRecipeViewTest(TestCase):
    """Tests for deleting recipes."""

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
            description='Test description',
            instructions='Step 1'
        )
        self.url = reverse('delete_recipe', kwargs={'recipe_id': self.recipe.id})

    def test_delete_recipe_url(self):
        self.assertEqual(self.url, f'/recipe/{self.recipe.id}/delete/')

    def test_delete_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_delete_recipe_via_post_by_author(self):
        self.client.login(username='@johndoe', password='Password123')
        before_count = Recipe.objects.count()
        response = self.client.post(self.url)
        after_count = Recipe.objects.count()
        self.assertEqual(before_count - 1, after_count)
        self.assertRedirects(response, reverse('welcome'))

    def test_delete_recipe_via_get_redirects_to_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        before_count = Recipe.objects.count()
        response = self.client.get(self.url)
        after_count = Recipe.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertRedirects(response, reverse('recipe', kwargs={'recipe_id': self.recipe.id}))

    def test_non_author_cannot_delete_recipe(self):
        self.client.login(username='@janedoe', password='Password123')
        before_count = Recipe.objects.count()
        response = self.client.post(self.url)
        after_count = Recipe.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_recipe_returns_404(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('delete_recipe', kwargs={'recipe_id': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_shows_success_message(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('deleted', str(messages[0]).lower())

