from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, RecipeIngredient, CuisineTag, DietaryTag
from recipes.forms import RecipeForm
from recipes.tests.helpers import reverse_with_next


class EditRecipeViewTest(TestCase):
    """Tests for editing recipes."""

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Original Recipe',
            description='Original description',
            instructions='Step 1\nStep 2'
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, name='Flour', amount=200, units='g'
        )
        self.url = reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id})
        self.form_input = {
            'recipe_name': 'Updated Recipe',
            'difficulty': 3,
            'description': 'Updated description',
            'ingredient_name_0': 'Sugar',
            'ingredient_amount_0': '100',
            'ingredient_units_0': 'g',
            'instruction_step_0': 'New step 1',
        }

    def test_url(self):
        self.assertEqual(self.url, f'/recipe/{self.recipe.id}/edit/')

    def test_redirect_when_logged_out(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_author_can_access(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_recipe.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RecipeForm)

    def test_shows_existing_data(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Original Recipe')
        self.assertContains(response, 'Original description')

    def test_shows_existing_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0]['name'], 'Flour')

    def test_non_author_gets_403(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_valid_post_updates_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, self.form_input)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, 'Updated Recipe')
        self.assertEqual(self.recipe.description, 'Updated description')
        self.assertRedirects(
            response, reverse('recipe', kwargs={'recipe_id': self.recipe.id})
        )

    def test_invalid_post_keeps_original(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['recipe_name'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, 'Original Recipe')

    def test_post_updates_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        self.client.post(self.url, self.form_input)
        ingredients = RecipeIngredient.objects.filter(recipe=self.recipe)
        self.assertEqual(ingredients.count(), 1)
        self.assertEqual(ingredients.first().name, 'Sugar')

    def test_post_saves_cuisine_tags(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.client.post(self.url, self.form_input)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.cuisine_tags.count(), 1)
        self.assertEqual(self.recipe.cuisine_tags.first().name, 'Italian')

    def test_post_saves_dietary_tags(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegan'
        self.client.post(self.url, self.form_input)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.dietary_tags.count(), 1)
        self.assertEqual(self.recipe.dietary_tags.first().name, 'Vegan')

    def test_nonexistent_recipe_404(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('edit_recipe', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_empty_ingredients_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_0'] = ''
        original_name = self.recipe.recipe_name
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_recipe.html')
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, original_name)
        self.assertIn('ingredient_error', response.context)
        self.assertEqual(response.context['ingredient_error'], 'At least one ingredient is required.')

    def test_post_with_empty_instructions_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_0'] = ''
        original_name = self.recipe.recipe_name
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_recipe.html')
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, original_name)
        self.assertIn('instruction_error', response.context)
        self.assertEqual(response.context['instruction_error'], 'At least one instruction is required.')

    def test_post_with_whitespace_only_ingredient_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['ingredient_name_0'] = '   '
        original_name = self.recipe.recipe_name
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, original_name)

    def test_post_with_whitespace_only_instruction_is_invalid(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_0'] = '   '
        original_name = self.recipe.recipe_name
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.recipe_name, original_name)


class EditRecipeDynamicTest(TestCase):
    """Tests for dynamic form actions when editing recipes."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Test Recipe',
            description='Test description',
            instructions='Step 1'
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, name='Flour', amount=200, units='g'
        )
        self.url = reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id})
        self.form_input = {
            'recipe_name': 'Test Recipe',
            'difficulty': 2,
            'description': 'Test description',
            'ingredient_name_0': 'Flour',
            'ingredient_amount_0': '200',
            'ingredient_units_0': 'g',
            'instruction_step_0': 'Step 1',
        }

    def test_add_ingredient(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_ingredient'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 2)

    def test_add_instruction(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_instruction'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instructions = response.context['instruction_steps']
        self.assertEqual(len(instructions), 2)

    def test_add_cuisine_tag(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_cuisine_tag'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        tags = response.context['cuisine_tags']
        self.assertEqual(len(tags), 2)

    def test_add_dietary_tag(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['add_dietary_tag'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        tags = response.context['dietary_tags']
        self.assertEqual(len(tags), 2)

    def test_delete_ingredient(self):
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

    def test_delete_instruction(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['instruction_step_1'] = 'Step 2'
        self.form_input['delete_instruction_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        instructions = response.context['instruction_steps']
        self.assertEqual(len(instructions), 1)
        self.assertEqual(instructions[0], 'Step 2')

    def test_delete_cuisine_tag(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['cuisine_tag_0'] = 'Italian'
        self.form_input['cuisine_tag_1'] = 'Mexican'
        self.form_input['delete_cuisine_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        tags = response.context['cuisine_tags']
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0], 'Mexican')

    def test_delete_dietary_tag(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['dietary_tag_0'] = 'Vegan'
        self.form_input['dietary_tag_1'] = 'Gluten-Free'
        self.form_input['delete_dietary_tag_0'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        tags = response.context['dietary_tags']
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0], 'Gluten-Free')

    def test_delete_last_ingredient_keeps_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_ingredient_0'] = ''
        response = self.client.post(self.url, self.form_input)
        ingredients = response.context['ingredients']
        self.assertEqual(len(ingredients), 1)

    def test_delete_last_instruction_keeps_empty(self):
        self.client.login(username='@johndoe', password='Password123')
        self.form_input['delete_instruction_0'] = ''
        response = self.client.post(self.url, self.form_input)
        instructions = response.context['instruction_steps']
        self.assertEqual(len(instructions), 1)

