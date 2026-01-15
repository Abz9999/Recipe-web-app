from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from recipes.models import Recipe, RecipeIngredient
from recipes.forms import RecipeForm
from recipes.tests.helpers import reverse_with_next


class CreateRecipeTestCase(TestCase):
    """Tests for the create recipe view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_recipe')
        User = get_user_model()
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'recipe_name': 'Pasta',
            'difficulty': 2,
            'description': 'Tomato penne pasta',
            'ingredient_name_0': 'Flour',
            'ingredient_amount_0': '200',
            'ingredient_units_0': 'g',
            'instruction_step_0': 'Mix ingredients',
        }

    def test_create_recipe_url(self):
        self.assertEqual(self.url, '/create_recipe/')

    def test_get_create_recipe_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipes.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, RecipeForm))
        self.assertFalse(form.is_bound)

    def test_post_with_valid_data_creates_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(before_count + 1, after_count)
        self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=302)

    def test_post_with_valid_data_sets_author(self):
        self.client.login(username='@johndoe', password='Password123')
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        self.assertEqual(recipe.author, self.user)

    def test_post_with_invalid_data_does_not_create_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['recipe_name'] = ''
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipes.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RecipeForm))
        self.assertTrue(form.is_bound)

    def test_post_with_missing_description_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['description'] = ''
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

    def test_post_saves_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        self.assertEqual(ingredients.count(), 1)
        ingredient = ingredients.first()
        self.assertEqual(ingredient.name, 'Flour')
        self.assertEqual(ingredient.amount, 200)
        self.assertEqual(ingredient.units, 'g')

    def test_post_saves_multiple_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_1'] = 'Eggs'
        self.form_input['ingredient_amount_1'] = '2'
        self.form_input['ingredient_units_1'] = 'pcs'
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        self.assertEqual(ingredients.count(), 2)

    def test_post_combines_instruction_steps(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_1'] = 'Bake for 20 minutes'
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        self.assertIn('Mix ingredients', recipe.instructions)
        self.assertIn('Bake for 20 minutes', recipe.instructions)

    def test_post_saves_cuisine_tags(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        self.assertEqual(recipe.cuisine_tags.count(), 1)
        self.assertEqual(recipe.cuisine_tags.first().name, 'Italian')

    def test_post_saves_dietary_tags(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegetarian'
        self.client.post(self.url, self.form_input)
        recipe = Recipe.objects.last()
        self.assertEqual(recipe.dietary_tags.count(), 1)
        self.assertEqual(recipe.dietary_tags.first().name, 'Vegetarian')

    def test_post_with_empty_ingredients_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_0'] = ''
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipes.html')
        self.assertIn('ingredient_error', response.context)
        self.assertEqual(response.context['ingredient_error'], 'At least one ingredient is required.')

    def test_post_with_empty_instructions_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_0'] = ''
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipes.html')
        self.assertIn('instruction_error', response.context)
        self.assertEqual(response.context['instruction_error'], 'At least one instruction is required.')

    def test_post_with_whitespace_only_ingredient_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_0'] = '   '
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

    def test_post_with_whitespace_only_instruction_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_0'] = '   '
        before_count = Recipe.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Recipe.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)


class CreateRecipeDynamicActionsTestCase(TestCase):
    """Tests for dynamic form actions (add/delete ingredients, instructions, tags)."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_recipe')
        User = get_user_model()
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'recipe_name': 'Pasta',
            'difficulty': 2,
            'description': 'Tomato penne pasta',
            'ingredient_name_0': 'Flour',
            'ingredient_amount_0': '200',
            'ingredient_units_0': 'g',
            'instruction_step_0': 'Mix ingredients',
        }

    def test_add_ingredient_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_ingredient'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_recipes.html')
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 2)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_add_instruction_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_instruction'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instruction_steps = response.context['instruction_steps']
        self.assertEqual(len(instruction_steps), 2)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_add_cuisine_tag_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_cuisine_tag'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        cuisine_tags = response.context['cuisine_tags']
        self.assertEqual(len(cuisine_tags), 2)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_add_dietary_tag_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_dietary_tag'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        dietary_tags = response.context['dietary_tags']
        self.assertEqual(len(dietary_tags), 2)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_delete_ingredient_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_1'] = 'Eggs'
        self.form_input['ingredient_amount_1'] = '2'
        self.form_input['ingredient_units_1'] = 'pcs'
        self.form_input['delete_ingredient_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0]['name'], 'Eggs')
        self.assertEqual(Recipe.objects.count(), 0)

    def test_delete_last_ingredient_keeps_one_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_ingredient_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)

    def test_delete_instruction_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_1'] = 'Bake for 20 minutes'
        self.form_input['delete_instruction_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instruction_steps = response.context['instruction_steps']
        self.assertEqual(len(instruction_steps), 1)
        self.assertEqual(instruction_steps[0], 'Bake for 20 minutes')
        self.assertEqual(Recipe.objects.count(), 0)

    def test_delete_last_instruction_keeps_one_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_instruction_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instruction_steps = response.context['instruction_steps']
        self.assertEqual(len(instruction_steps), 1)

    def test_delete_cuisine_tag_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.form_input['cuisine_tag_1'] = 'Mexican'
        self.form_input['delete_cuisine_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        cuisine_tags = response.context['cuisine_tags']
        self.assertEqual(len(cuisine_tags), 1)
        self.assertEqual(cuisine_tags[0], 'Mexican')
        self.assertEqual(Recipe.objects.count(), 0)

    def test_delete_last_cuisine_tag_keeps_one_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.form_input['delete_cuisine_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        cuisine_tags = response.context['cuisine_tags']
        self.assertEqual(len(cuisine_tags), 1)

    def test_delete_dietary_tag_action(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegetarian'
        self.form_input['dietary_tag_1'] = 'Vegan'
        self.form_input['delete_dietary_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        dietary_tags = response.context['dietary_tags']
        self.assertEqual(len(dietary_tags), 1)
        self.assertEqual(dietary_tags[0], 'Vegan')
        self.assertEqual(Recipe.objects.count(), 0)

    def test_delete_last_dietary_tag_keeps_one_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegetarian'
        self.form_input['delete_dietary_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        dietary_tags = response.context['dietary_tags']
        self.assertEqual(len(dietary_tags), 1)

    def test_delete_ingredient_out_of_bounds_does_nothing(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_ingredient_99'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)

    def test_delete_instruction_out_of_bounds_does_nothing(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_instruction_99'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instruction_steps = response.context['instruction_steps']
        self.assertEqual(len(instruction_steps), 1)

    def test_delete_cuisine_tag_out_of_bounds_does_nothing(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.form_input['delete_cuisine_tag_99'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        cuisine_tags = response.context['cuisine_tags']
        self.assertEqual(len(cuisine_tags), 1)
        self.assertEqual(cuisine_tags[0], 'Italian')

    def test_delete_dietary_tag_out_of_bounds_does_nothing(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegetarian'
        self.form_input['delete_dietary_tag_99'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        dietary_tags = response.context['dietary_tags']
        self.assertEqual(len(dietary_tags), 1)
        self.assertEqual(dietary_tags[0], 'Vegetarian')
