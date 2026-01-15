from django.test import TestCase
from recipes.models import User, Recipe
from recipes.helpers import build_recipe_list


class BuildRecipeListTest(TestCase):
    """Test suite for build_recipe_list helper function."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User'
        )
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            recipe_name='Recipe 1',
            description='Description 1'
        )
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            recipe_name='Recipe 2',
            description='Description 2'
        )

    def test_build_recipe_list_with_empty_recipes(self):
        result = build_recipe_list([], set())
        self.assertEqual(result, [])

    def test_build_recipe_list_with_empty_favourites(self):
        recipes = [self.recipe1, self.recipe2]
        result = build_recipe_list(recipes, set())

        self.assertEqual(len(result), 2)
        self.assertFalse(result[0]['is_favourite'])
        self.assertFalse(result[1]['is_favourite'])

    def test_build_recipe_list_with_all_favourited(self):
        recipes = [self.recipe1, self.recipe2]
        favourite_ids = {self.recipe1.id, self.recipe2.id}
        result = build_recipe_list(recipes, favourite_ids)

        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['is_favourite'])
        self.assertTrue(result[1]['is_favourite'])

    def test_build_recipe_list_with_some_favourited(self):
        recipes = [self.recipe1, self.recipe2]
        favourite_ids = {self.recipe1.id}
        result = build_recipe_list(recipes, favourite_ids)

        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['is_favourite'])
        self.assertFalse(result[1]['is_favourite'])

    def test_build_recipe_list_returns_correct_recipe_objects(self):
        recipes = [self.recipe1, self.recipe2]
        result = build_recipe_list(recipes, set())

        self.assertEqual(result[0]['recipe'], self.recipe1)
        self.assertEqual(result[1]['recipe'], self.recipe2)

    def test_build_recipe_list_with_non_matching_favourite_ids(self):
        recipes = [self.recipe1, self.recipe2]
        favourite_ids = {9999, 8888}
        result = build_recipe_list(recipes, favourite_ids)

        self.assertEqual(len(result), 2)
        self.assertFalse(result[0]['is_favourite'])
        self.assertFalse(result[1]['is_favourite'])


