"""Tests for the other user profile view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Follow, Recipe
from recipes.tests.helpers import reverse_with_next


class OtherUserProfileViewTest(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('user_profile', kwargs={'user_id': self.other_user.id})

    def test_other_user_profile_url_pattern(self):
        self.assertEqual(self.url, f'/user/{self.other_user.id}/')

    def test_other_user_profile_uses_correct_template(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'other_user_profile.html')

    def test_other_user_profile_has_correct_context(self):
        self._login_user()
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['profile_user'], self.other_user)
        self.assertFalse(context['is_own_profile'])

    def test_other_user_profile_shows_user_recipes(self):
        self._login_user()
        Recipe.objects.create(
            author=self.other_user,
            recipe_name='Other User Recipe',
            description='Recipe by other user'
        )
        response = self.client.get(self.url)
        self.assertIn('user_recipes', response.context)
        user_recipes = response.context['user_recipes']
        self.assertEqual(user_recipes.first().author, self.other_user)

    def test_is_following_context_when_not_following(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertFalse(response.context['is_following'])

    def test_is_following_context_when_following(self):
        self._login_user()
        Follow.objects.create(follower=self.user, following=self.other_user)
        response = self.client.get(self.url)
        self.assertTrue(response.context['is_following'])

    def test_other_user_profile_requires_authentication(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_nonexistent_user_profile_returns_404(self):
        self._login_user()
        nonexistent_url = reverse('user_profile', kwargs={'user_id': 9999})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

    def test_other_user_profile_counts_are_correct(self):
        self._login_user()
        Follow.objects.create(follower=self.user, following=self.other_user)
        new_user = User.objects.create_user(
            username='@newuser',
            email='new@example.com',
            password='Password123'
        )
        Follow.objects.create(follower=new_user, following=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context['followers_count'], 2)
        self.assertEqual(response.context['following_count'], 0)

    def test_pagination_shows_12_recipes_per_page(self):
        self._login_user()
        self._create_recipes_for_user(self.other_user, 15)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['page_obj']), 12)

    def test_pagination_second_page(self):
        self._login_user()
        self._create_recipes_for_user(self.other_user, 15)
        response = self.client.get(f'{self.url}?page=2')
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_invalid_page_parameter_handled(self):
        self._login_user()
        self._create_recipes_for_user(self.other_user, 10)
        response = self.client.get(f'{self.url}?page=invalid')
        self.assertEqual(response.context['page_obj'].number, 1)

    def test_no_recipes_shows_empty_message(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipes_count'], 0)
        self.assertContains(response, "hasn't shared any recipes")

    def _login_user(self):
        self.client.login(username=self.user.username, password='Password123')

    def _create_recipes_for_user(self, user, count):
        for i in range(count):
            Recipe.objects.create(
                author=user,
                recipe_name=f'Recipe {i}',
                description=f'Description {i}'
            )
