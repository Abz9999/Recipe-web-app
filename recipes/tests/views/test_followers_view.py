"""Tests for the followers view."""
from django.test import TestCase
from django.urls import reverse
from recipes.models import User
from recipes.tests.helpers import reverse_with_next


class FollowUserViewTest(TestCase):
    """Tests for following users."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('follow_user', kwargs={'user_id': self.other_user.id})

    def test_follow_user_url(self):
        self.assertEqual(self.url, f'/user/{self.other_user.id}/follow/')

    def test_follow_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_follow_user_success(self):
        self.client.login(username='@johndoe', password='Password123')
        self.assertFalse(self.user.is_following(self.other_user))
        response = self.client.get(self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_following(self.other_user))
        self.assertRedirects(
            response, reverse('user_profile', kwargs={'user_id': self.other_user.id})
        )

    def test_follow_user_already_following(self):
        self.client.login(username='@johndoe', password='Password123')
        self.user.follow(self.other_user)
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('already', str(messages[0]).lower())

    def test_cannot_follow_self(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('follow_user', kwargs={'user_id': self.user.id})
        response = self.client.get(url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('yourself', str(messages[0]).lower())

    def test_follow_nonexistent_user_returns_404(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('follow_user', kwargs={'user_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UnfollowUserViewTest(TestCase):
    """Tests for unfollowing users."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.url = reverse('unfollow_user', kwargs={'user_id': self.other_user.id})

    def test_unfollow_user_url(self):
        self.assertEqual(self.url, f'/user/{self.other_user.id}/unfollow/')

    def test_unfollow_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_unfollow_user_success(self):
        self.client.login(username='@johndoe', password='Password123')
        self.user.follow(self.other_user)
        self.assertTrue(self.user.is_following(self.other_user))
        response = self.client.get(self.url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_following(self.other_user))
        self.assertRedirects(
            response, reverse('user_profile', kwargs={'user_id': self.other_user.id})
        )

    def test_unfollow_user_not_following(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('not following', str(messages[0]).lower())

    def test_cannot_unfollow_self(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('unfollow_user', kwargs={'user_id': self.user.id})
        response = self.client.get(url, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('yourself', str(messages[0]).lower())

    def test_unfollow_nonexistent_user_returns_404(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('unfollow_user', kwargs={'user_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


