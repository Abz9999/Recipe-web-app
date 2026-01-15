from django.test import TestCase
from recipes.forms import RecipeForm
from recipes.models import Recipe, User


class RecipeFormTestCase(TestCase):

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
        self.form_input = {
            'recipe_name': 'Pasta',
            'difficulty': 2,
            'instructions': '1. step1 \n 2.step 2',
            'description': 'tomato penne pasta',
        }

    def test_form_has_necessary_fields(self):
        form = RecipeForm()
        self.assertIn('recipe_name', form.fields)
        self.assertIn('difficulty', form.fields)
        self.assertIn('instructions', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('image', form.fields)

    def test_valid_form(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_blank_recipe_name_is_invalid(self):
        self.form_input['recipe_name'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_recipe_name_is_invalid(self):
        self.form_input['recipe_name'] = 'x' * 256
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_description_is_invalid(self):
        self.form_input['description'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_instructions_is_invalid(self):
        self.form_input['instructions'] = ''
        form = RecipeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = RecipeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        before_count = Recipe.objects.count()
        recipe = form.save(commit=False)
        recipe.author = self.user
        form.save()
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def test_get_image_filename_returns_none_for_new_form(self):
        form = RecipeForm()
        self.assertIsNone(form.get_image_filename())

    def test_get_image_filename_returns_none_for_recipe_without_image(self):
        form = RecipeForm(instance=self.recipe)
        self.assertIsNone(form.get_image_filename())

    def test_get_image_filename_returns_filename_for_recipe_with_image(self):
        self.recipe.image = 'recipes/test_image.jpg'
        self.recipe.save()
        form = RecipeForm(instance=self.recipe)
        self.assertEqual(form.get_image_filename(), 'test_image.jpg')
