"""Tests for the profile page view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Follow, Recipe, Rating
from recipes.tests.helpers import reverse_with_next


class ProfilePageViewTest(TestCase):
    """Test suite for the profile page view."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('profile_page')
        
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            recipe_name='Chocolate Cake',
            description='Delicious chocolate cake'
        )
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            recipe_name='Vanilla Cupcakes',
            description='Sweet vanilla cupcakes'
        )
        
        Follow.objects.create(follower=self.other_user, following=self.user)
        Follow.objects.create(follower=self.user, following=self.other_user)

        Rating.objects.create(user=self.other_user, recipe=self.recipe1, rating=5)
        Rating.objects.create(user=self.other_user, recipe=self.recipe2, rating=3)
   
    def test_profile_page_url(self):
        self.assertEqual(self.url, '/profile_page/')

    def test_profile_page_requires_authentication(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        
        self.assertRedirects(response, redirect_url, status_code=302)
    
    def test_profile_page_loads_when_authenticated(self):
        self._login_user()
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')

    def test_profile_page_has_correct_user_context(self):
        self._login_user()
        response = self.client.get(self.url)
        context = response.context
        
        self.assertEqual(context['profile_user'], self.user)
        self.assertTrue(context['is_own_profile'])

    def test_profile_page_shows_user_recipes(self):
        self._login_user()
        response = self.client.get(self.url)
        
        user_recipes = response.context['user_recipes']
        self.assertEqual(len(user_recipes), 2)
        self.assertIn(self.recipe1, user_recipes)
        self.assertIn(self.recipe2, user_recipes)

    def test_profile_page_shows_correct_counts(self):
        self._login_user()
        response = self.client.get(self.url)
        context = response.context
        
        self.assertEqual(context['recipes_count'], 2)
        self.assertEqual(context['followers_count'], 1)
        self.assertEqual(context['following_count'], 1)

    def test_profile_page_shows_followers_and_following(self):
        self._login_user()
        response = self.client.get(self.url)
        context = response.context
        
        self.assertIn(self.other_user, context['followers'])
        self.assertIn(self.other_user, context['following'])

    def test_profile_page_with_recipes_tab(self):
        self._login_user()
        response = self.client.get(f'{self.url}?tab=recipes')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'recipes')
        self.assertContains(response, 'Chocolate Cake')
        self.assertContains(response, 'Vanilla Cupcakes')

    def test_profile_page_with_favourites_tab(self):
        self._login_user()
        self.user.favourite_recipe(self.recipe1)
        
        response = self.client.get(f'{self.url}?tab=favourites')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'favourites')
        self.assertEqual(len(response.context['favourites']), 1)

    def test_profile_page_with_followers_tab(self):
        self._login_user()
        response = self.client.get(f'{self.url}?tab=followers')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'followers')
        self.assertContains(response, '@janedoe')

    def test_profile_page_with_following_tab(self):
        self._login_user()
        response = self.client.get(f'{self.url}?tab=following')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'following')
        self.assertContains(response, '@janedoe')

    def test_profile_page_with_invalid_tab(self):
        self._login_user()
        response = self.client.get(f'{self.url}?tab=invalid')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'invalid')

    def test_favourites_count_updates_when_recipe_favourited(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(response.context['favourites_count'], 0)
        
        self.user.favourite_recipe(self.recipe1)
        response = self.client.get(self.url)
        self.assertEqual(response.context['favourites_count'], 1)
        
        self.user.favourite_recipe(self.recipe2)
        response = self.client.get(self.url)
        self.assertEqual(response.context['favourites_count'], 2)

    def test_favourites_tab_shows_only_user_favourites(self):
        self._login_user()
        
        # Current user favourites recipe1
        self.user.favourite_recipe(self.recipe1)
        # Other user favourites recipe2
        self.other_user.favourite_recipe(self.recipe2)
        
        response = self.client.get(f'{self.url}?tab=favourites')
        favourites = response.context['favourites']
        
        self.assertEqual(len(favourites), 1)
        self.assertIn(self.recipe1, favourites)
        self.assertNotIn(self.recipe2, favourites)

    def test_favourites_tab_empty_state(self):
        self._login_user()
        response = self.client.get(f'{self.url}?tab=favourites')
        
        self.assertEqual(len(response.context['favourites']), 0)
        self.assertEqual(response.context['favourites_count'], 0)
        self.assertContains(response, 'No favourite recipes yet')
    
    def test_profile_page_user_with_no_recipes(self):
        new_user = self._create_test_user('@norecipes')
        self.client.login(username='@norecipes', password='Password123')
        
        response = self.client.get(reverse('profile_page'))
        
        self.assertEqual(response.context['recipes_count'], 0)
        self.assertEqual(len(response.context['user_recipes']), 0)

    def test_profile_page_user_with_no_follows(self):
        new_user = self._create_test_user('@nofollows')
        self.client.login(username='@nofollows', password='Password123')
        
        response = self.client.get(reverse('profile_page'))
        
        self.assertEqual(response.context['followers_count'], 0)
        self.assertEqual(response.context['following_count'], 0)
    
    def test_recipes_tab_pagination_default_page(self):
        self._login_user()
        # Start with 2 existing recipes, add 4 more
        self._create_additional_recipes_for_user(self.user, 4)
        
        response = self.client.get(f'{self.url}?tab=recipes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_tab'], 'recipes')
        self.assertEqual(response.context['recipes_page_obj'].number, 1)
        # 6 total recipes exactly fills page 1
        self.assertEqual(len(response.context['recipes_page_obj']), 6)
        self.assertEqual(response.context['recipes_count'], 6)

    def test_recipes_tab_pagination_second_page(self):
        self._login_user()
        self._create_additional_recipes_for_user(self.user, 6)
        
        response = self.client.get(f'{self.url}?tab=recipes&recipes_page=2')
        self.assertEqual(response.context['selected_tab'], 'recipes')
        self.assertEqual(response.context['recipes_page_obj'].number, 2)
        self.assertEqual(len(response.context['recipes_page_obj']), 2)

    def test_favourites_tab_pagination_default_page(self):
        self._login_user()
        # Favourite the 2 existing recipes
        self.user.favourite_recipe(self.recipe1)
        self.user.favourite_recipe(self.recipe2)
        self._create_and_favourite_recipes(4)
        
        response = self.client.get(f'{self.url}?tab=favourites')
        self.assertEqual(response.context['selected_tab'], 'favourites')
        self.assertEqual(response.context['favourites_page_obj'].number, 1)
        self.assertEqual(len(response.context['favourites_page_obj']), 6)

    def test_favourites_tab_pagination_second_page(self):
        self._login_user()
        self.user.favourite_recipe(self.recipe1)
        self.user.favourite_recipe(self.recipe2)
        self._create_and_favourite_recipes(6)
        
        response = self.client.get(f'{self.url}?tab=favourites&favourites_page=2')
        self.assertEqual(response.context['selected_tab'], 'favourites')
        self.assertEqual(response.context['favourites_page_obj'].number, 2)
        self.assertEqual(len(response.context['favourites_page_obj']), 2)

    def test_pagination_preserves_tab_state(self):
        self._login_user()
        self._create_additional_recipes_for_user(self.user, 8)
        
        response = self.client.get(f'{self.url}?tab=recipes&recipes_page=2')
        self.assertContains(response, 'href="?tab=recipes&recipes_page=1#recipes"')

    def test_no_pagination_when_under_limit(self):
        self._login_user()
        self._create_additional_recipes_for_user(self.user, 1)
        
        response = self.client.get(f'{self.url}?tab=recipes')
        self.assertEqual(response.context['recipes_page_obj'].paginator.num_pages, 1)
        
    def test_invalid_recipes_page_handled(self):
        self._login_user()
        self._create_additional_recipes_for_user(self.user, 8)
        
        response = self.client.get(f'{self.url}?tab=recipes&recipes_page=invalid')
        self.assertEqual(response.context['recipes_page_obj'].number, 1)

    def test_invalid_favourites_page_handled(self):
        self._login_user()
        self.user.favourite_recipe(self.recipe1)
        self.user.favourite_recipe(self.recipe2)
        self._create_and_favourite_recipes(8)
        
        response = self.client.get(f'{self.url}?tab=favourites&favourites_page=invalid')
        self.assertEqual(response.context['favourites_page_obj'].number, 1)
    
    def _login_user(self):
        self.client.login(username=self.user.username, password='Password123')
    
    def _create_test_user(self, username):
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )
    
    def _create_recipes_for_user(self, user, count):
        """Create multiple recipes for a user."""
        for i in range(count):
            Recipe.objects.create(
                author=user,
                recipe_name=f'Recipe {i}',
                description=f'Description {i}'
            )
    
    def _create_and_favourite_recipes(self, count):
        """Create recipes and favourite them for current user."""
        for i in range(count):
            recipe = Recipe.objects.create(
                author=self.other_user,
                recipe_name=f'Favourite Recipe {i}',
                description=f'Description {i}'
            )
            self.user.favourite_recipe(recipe)
    
    def _create_additional_recipes_for_user(self, user, count):
        """Create additional recipes for a user (adds to existing)."""
        current_count = Recipe.objects.filter(author=user).count()
        
        for i in range(count):
            Recipe.objects.create(
                author=user,
                recipe_name=f'Recipe {current_count + i}',
                description=f'Description {current_count + i}'
            )