from django.test import TestCase
from recipes.models import User, Recipe
from recipes.models.favourite import Favourite


class FavouriteModelTestCase(TestCase):
    """Unit tests for the Favourite model and related User methods."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Chocolate Cake',
            difficulty=3,
            description='A delicious chocolate cake recipe',
            instructions='Step 1. Mix ingredients.\nStep 2. Bake at 180C.'
        )
        self.recipe2 = Recipe.objects.create(
            author=self.other_user,
            recipe_name='Vanilla Cupcakes',
            difficulty=2,
            description='Light and fluffy vanilla cupcakes',
            instructions='Step 1. Cream butter and sugar.\nStep 2. Add flour.'
        )

    def test_favourite_recipe(self):
        self.assertFalse(self.user.has_favourited(self.recipe))
        self.user.favourite_recipe(self.recipe)
        self.assertTrue(self.user.has_favourited(self.recipe))

    def test_favourite_recipe_is_idempotent(self):
        self.user.favourite_recipe(self.recipe)
        self.user.favourite_recipe(self.recipe)
        self.assertTrue(self.user.has_favourited(self.recipe))
        self.assertEqual(self.user.get_favourites_count(), 1)

    def test_unfavourite_recipe_removes_from_favourites(self):
        self.user.favourite_recipe(self.recipe)
        self.user.unfavourite_recipe(self.recipe)
        self.assertFalse(self.user.has_favourited(self.recipe))

    def test_unfavourite_recipe_when_not_favourited(self):
        self.user.unfavourite_recipe(self.recipe)
        self.assertFalse(self.user.has_favourited(self.recipe))

    def test_get_favourites(self):
        self.user.favourite_recipe(self.recipe)
        self.user.favourite_recipe(self.recipe2)
        favourites = self.user.get_favourites()
        self.assertEqual(len(favourites), 2)
        self.assertIn(self.recipe, favourites)
        self.assertIn(self.recipe2, favourites)

    def test_get_favourites_count(self):
        self.assertEqual(self.user.get_favourites_count(), 0)
        self.user.favourite_recipe(self.recipe)
        self.assertEqual(self.user.get_favourites_count(), 1)
        self.user.favourite_recipe(self.recipe2)
        self.assertEqual(self.user.get_favourites_count(), 2)

    def test_has_favourited(self):
        self.assertFalse(self.user.has_favourited(self.recipe))
        self.user.favourite_recipe(self.recipe)
        self.assertTrue(self.user.has_favourited(self.recipe))

    def test_user_can_favourite_own_recipe(self):
        self.user.favourite_recipe(self.recipe)
        self.assertTrue(self.user.has_favourited(self.recipe))

    def test_multiple_users_can_favourite_same_recipe(self):
        self.user.favourite_recipe(self.recipe)
        self.other_user.favourite_recipe(self.recipe)
        self.assertTrue(self.user.has_favourited(self.recipe))
        self.assertTrue(self.other_user.has_favourited(self.recipe))
        self.assertEqual(self.user.get_favourites_count(), 1)
        self.assertEqual(self.other_user.get_favourites_count(), 1)

    def test_favourite_str(self):
        self.user.favourite_recipe(self.recipe)
        favourite = Favourite.objects.get(user=self.user, recipe=self.recipe)
        expected = f"{self.user.username} favourited {self.recipe.recipe_name}"
        self.assertEqual(str(favourite), expected)
