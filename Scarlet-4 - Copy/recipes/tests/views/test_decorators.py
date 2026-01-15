from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe
from recipes.views.decorators import LoginProhibitedMixin


class LoginProhibitedMixinTest(TestCase):
    """Tests for the LoginProhibitedMixin."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def test_get_redirect_url_raises_when_not_configured(self):
        mixin = LoginProhibitedMixin()
        with self.assertRaises(ImproperlyConfigured):
            mixin.get_redirect_when_logged_in_url()

    def test_get_redirect_url_returns_configured_url(self):
        mixin = LoginProhibitedMixin()
        mixin.redirect_when_logged_in_url = 'welcome'
        self.assertEqual(mixin.get_redirect_when_logged_in_url(), 'welcome')

    def test_dispatch_redirects_authenticated_user(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('log_in'))
        self.assertRedirects(response, reverse('welcome'))

    def test_dispatch_allows_unauthenticated_user(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)


class LoginProhibitedDecoratorTest(TestCase):
    """Tests for the login_prohibited decorator."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def test_unauthenticated_user_can_access(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_is_redirected(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('welcome'))


class AuthorRequiredDecoratorTest(TestCase):
    """Tests for the author_required decorator."""

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

    def test_author_can_access(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_author_gets_forbidden(self):
        self.client.login(username='@janedoe', password='Password123')
        url = reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_nonexistent_recipe_returns_404(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('edit_recipe', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
