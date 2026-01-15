from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from recipes.models import User, Recipe, Rating


class RatingModelTestCase(TestCase):
    """Unit tests for the Rating model."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Chocolate Cake',
            difficulty=3,
            description='A delicious chocolate cake recipe',
            instructions='Step 1. Mix ingredients.\nStep 2. Bake at 180C.'
        )
        self.rating = Rating.objects.create(
            recipe=self.recipe,
            user=self.user,
            rating=4
        )

    def test_valid_rating_is_valid(self):
        self.assert_rating_is_valid()

    def test_rating_cannot_exceed_5(self):
        self.rating.rating = 6
        self.assert_rating_is_invalid()

    def test_rating_cannot_be_less_than_1(self):
        self.rating.rating = 0
        self.assert_rating_is_invalid()

    def test_rating_can_be_5(self):
        self.rating.rating = 5
        self.assert_rating_is_valid()

    def test_rating_can_be_1(self):
        self.rating.rating = 1
        self.assert_rating_is_valid()

    def test_user_cannot_rate_same_recipe_twice(self):
        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                recipe=self.recipe,
                user=self.user,
                rating=5
            )

    def test_rating_deletes_on_recipe_delete(self):
        self.assertTrue(Rating.objects.filter(pk=self.rating.pk).exists())
        self.recipe.delete()
        self.assertFalse(Rating.objects.filter(pk=self.rating.pk).exists())

    def test_rating_deletes_on_user_delete(self):
        self.assertTrue(Rating.objects.filter(pk=self.rating.pk).exists())
        self.user.delete()
        self.assertFalse(Rating.objects.filter(pk=self.rating.pk).exists())

    def test_str(self):
        expected = f"{self.user} rated '{self.recipe}' {self.rating.rating}/5"
        self.assertEqual(str(self.rating), expected)

    def assert_rating_is_valid(self):
        try:
            self.rating.full_clean()
        except ValidationError:
            self.fail('Test rating should be valid')

    def assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating.full_clean()
