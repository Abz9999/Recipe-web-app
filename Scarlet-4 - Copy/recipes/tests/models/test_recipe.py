from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import Recipe, User, CuisineTag, DietaryTag, Rating


class RecipeTestCase(TestCase):
    """Unit tests for the Recipe model."""

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

    def test_valid_recipe_is_valid(self):
        self.assert_recipe_is_valid()

    def test_recipe_with_blank_recipe_name_is_invalid(self):
        self.recipe.recipe_name = ''
        self.assert_recipe_is_invalid()

    def test_recipe_with_overlong_recipe_name_is_invalid(self):
        self.recipe.recipe_name = 'x' * 256
        self.assert_recipe_is_invalid()

    def test_recipe_with_blank_description_is_invalid(self):
        self.recipe.description = ''
        self.assert_recipe_is_invalid()

    def test_recipe_with_blank_instructions_is_invalid(self):
        self.recipe.instructions = ''
        self.assert_recipe_is_invalid()

    def test_recipe_can_have_no_tags(self):
        self.assertEqual(self.recipe.cuisine_tags.count(), 0)
        self.assertEqual(self.recipe.dietary_tags.count(), 0)

    def test_recipe_can_have_cuisine_tag(self):
        tag = CuisineTag.objects.create(name='Italian')
        self.recipe.cuisine_tags.add(tag)
        self.assertEqual(self.recipe.cuisine_tags.count(), 1)
        self.assertIn(tag, self.recipe.cuisine_tags.all())

    def test_recipe_can_have_dietary_tag(self):
        tag = DietaryTag.objects.create(name='Vegan')
        self.recipe.dietary_tags.add(tag)
        self.assertEqual(self.recipe.dietary_tags.count(), 1)
        self.assertIn(tag, self.recipe.dietary_tags.all())

    def test_recipe_can_have_multiple_tags(self):
        cuisine = CuisineTag.objects.create(name='Mexican')
        dietary = DietaryTag.objects.create(name='Gluten-Free')
        self.recipe.cuisine_tags.add(cuisine)
        self.recipe.dietary_tags.add(dietary)
        self.assertEqual(self.recipe.cuisine_tags.count(), 1)
        self.assertEqual(self.recipe.dietary_tags.count(), 1)

    def test_average_rating_with_no_ratings(self):
        self.assertIsNone(self.recipe.average_rating())

    def test_average_rating_with_one_rating(self):
        Rating.objects.create(recipe=self.recipe, user=self.user, rating=4)
        self.assertEqual(self.recipe.average_rating(), 4.0)

    def test_average_rating_with_multiple_ratings(self):
        Rating.objects.create(recipe=self.recipe, user=self.user, rating=4)
        Rating.objects.create(recipe=self.recipe, user=self.other_user, rating=5)
        self.assertEqual(self.recipe.average_rating(), 4.5)

    def assert_recipe_is_valid(self):
        try:
            self.recipe.full_clean()
        except ValidationError:
            self.fail('Test recipe should be valid')

    def assert_recipe_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.recipe.full_clean()
