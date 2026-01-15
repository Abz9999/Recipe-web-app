from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import RecipeIngredient, Recipe, User


class RecipeIngredientTestCase(TestCase):
    """Unit tests for the RecipeIngredient model."""

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
        self.ingredient = RecipeIngredient(
            recipe=self.recipe,
            name='Sugar',
            amount=100,
            units='g'
        )

    def test_valid_ingredient_is_valid(self):
        self.assert_ingredient_is_valid()

    def test_ingredient_with_blank_name_is_invalid(self):
        self.ingredient.name = ''
        self.assert_ingredient_is_invalid()

    def test_ingredient_with_overlong_name_is_invalid(self):
        self.ingredient.name = 'x' * 256
        self.assert_ingredient_is_invalid()

    def test_ingredient_with_zero_amount_is_invalid(self):
        self.ingredient.amount = 0
        self.assert_ingredient_is_invalid()

    def test_str_method(self):
        self.ingredient.save()
        expected = f"{self.ingredient.amount}{self.ingredient.units} {self.ingredient.name}"
        self.assertEqual(str(self.ingredient), expected)

    def assert_ingredient_is_valid(self):
        try:
            self.ingredient.full_clean()
        except ValidationError:
            self.fail('Test ingredient should be valid')

    def assert_ingredient_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.ingredient.full_clean()
