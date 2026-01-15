from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, Rating, RecipeIngredient
from recipes.forms import RatingForm
from recipes.tests.helpers import reverse_with_next


class WelcomeViewTestCase(TestCase):
    """ Test suite for the welcome view. """

    fixtures = [
        'recipes/tests/fixtures/default_user.json',
        'recipes/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.testUser = User.objects.create_user(username='@testuser2', password='Password123')
        self.url = reverse('welcome')
        
        self.highRatedRecipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Chocolate Cake',
            description="Easy to make and sweet"
        )
        RecipeIngredient.objects.create(recipe=self.highRatedRecipe, name='sugar', amount=100, units='g')
        RecipeIngredient.objects.create(recipe=self.highRatedRecipe, name='eggs', amount=2, units='g')
        RecipeIngredient.objects.create(recipe=self.highRatedRecipe, name='flour', amount=200, units='g')
        RecipeIngredient.objects.create(recipe=self.highRatedRecipe, name='chocolate', amount=10, units='g')
        
        self.midRatedRecipe = Recipe.objects.create(
            author=self.testUser,
            recipe_name='Tuna Pasta',
            description="Quick lunchtime meal"
        )
        RecipeIngredient.objects.create(recipe=self.midRatedRecipe, name='pasta', amount=250, units='g')
        RecipeIngredient.objects.create(recipe=self.midRatedRecipe, name='tuna', amount=150, units='g')
        RecipeIngredient.objects.create(recipe=self.midRatedRecipe, name='sweetcorn', amount=100, units='g')
        
        self.lowRatedRecipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Vanilla Cupcakes',
            description="Light and fluffy"
        )
        RecipeIngredient.objects.create(recipe=self.lowRatedRecipe, name='sugar', amount=150, units='g')
        RecipeIngredient.objects.create(recipe=self.lowRatedRecipe, name='flour', amount=200, units='g')
        RecipeIngredient.objects.create(recipe=self.lowRatedRecipe, name='vanilla extract', amount=5, units='ml')

        Rating.objects.create(user=self.user, recipe = self.highRatedRecipe, rating=5)
        Rating.objects.create(user=self.testUser, recipe = self.highRatedRecipe, rating = 5)

        Rating.objects.create(user=self.user, recipe = self.midRatedRecipe, rating=3)
        Rating.objects.create(user=self.testUser, recipe = self.midRatedRecipe, rating = 4)
    
    def test_welcome_view_url(self):
        self.assertEqual(self.url,'/welcome/')

    def test_get_welcome_view(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome.html')

    def test_sort_by_highest_rated(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'sort': 'highest'})
        context_data = response.context['recipe_data']

        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Chocolate Cake')
        self.assertEqual(context_data[1]['recipe'].recipe_name, 'Tuna Pasta')
        self.assertEqual(context_data[2]['recipe'].recipe_name, 'Vanilla Cupcakes')

    def test_sort_by_lowest_rated(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'sort': 'lowest'})
        context_data = response.context['recipe_data']

        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Vanilla Cupcakes')
        self.assertEqual(context_data[1]['recipe'].recipe_name, 'Tuna Pasta')
        self.assertEqual(context_data[2]['recipe'].recipe_name, 'Chocolate Cake')

    def test_search_by_recipe_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'q': 'Pasta'})
        context_data = response.context['recipe_data']

        self.assertEqual(len(response.context['recipe_data']),1)
        self.assertContains(response, 'Tuna Pasta')

    def test_search_by_ingredient(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'q': 'vanilla'})
        context_data = response.context['recipe_data']
        
        self.assertEqual(len(response.context['recipe_data']),1)
        self.assertContains(response, 'Vanilla Cupcakes')
    
    def test_search_by_author(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'q': '@testuser2'})
        context_data = response.context['recipe_data']

        self.assertEqual(len(response.context['recipe_data']),1)
        self.assertContains(response, 'Tuna Pasta')

    def test_stars_for_no_ratings(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        context_data = response.context['recipe_data']

        recipe_data = [item for item in context_data if item['recipe'].recipe_name == "Vanilla Cupcakes"][0]
        
        self.assertIsNone(recipe_data['avg'])
        self.assertEqual(recipe_data['stars'],[])

    def test_rating_form_when_rated_by_authenticated_user(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        context_data = response.context['recipe_data']

        recipe_data = [item for item in context_data if item['recipe'].recipe_name == "Chocolate Cake"][0]
        form = recipe_data['rating_form']
        self.assertIsInstance(form, RatingForm)
        self.assertEqual(form['rating'].value(), 5)
    
    def test_rating_form_when_unrated_by_authenticated_user(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        context_data = response.context['recipe_data']

        recipe_data = [item for item in context_data if item['recipe'].recipe_name == "Vanilla Cupcakes"][0]
        form = recipe_data['rating_form']
        self.assertIsInstance(form, RatingForm)
        self.assertFalse(form.is_bound)

    def test_rating_form_when_user_logged_out(self):
        self.client.logout()
        response = self.client.get(self.url)
        context_data = response.context['recipe_data']

        for item in context_data:
            self.assertIsNone(item['rating_form'])

    def test_cuisine_tag_filter(self):
        from recipes.models import CuisineTag
        tag = CuisineTag.objects.create(name='Italian')
        self.highRatedRecipe.cuisine_tags.add(tag)
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'cuisine_tags': 'Italian'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Chocolate Cake')

    def test_dietary_tag_filter(self):
        from recipes.models import DietaryTag
        tag = DietaryTag.objects.create(name='Vegan')
        self.midRatedRecipe.dietary_tags.add(tag)
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'dietary_tags': 'Vegan'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Tuna Pasta')

    def test_missing_cuisine_tag_shows_nothing(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'cuisine_tags': 'NonExistent'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 0)

    def test_missing_dietary_tag_shows_nothing(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'dietary_tags': 'NonExistent'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 0)

    def test_following_filter(self):
        self.user.follow(self.testUser)
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'filter': 'following'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Tuna Pasta')

    def test_pagination_keeps_query_params(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'q': 'test', 'page': '1'})
        self.assertIn('page_url_prefix', response.context)

    def test_combined_tag_filters(self):
        from recipes.models import CuisineTag, DietaryTag
        cuisine = CuisineTag.objects.create(name='Mexican')
        dietary = DietaryTag.objects.create(name='Gluten-Free')
        self.lowRatedRecipe.cuisine_tags.add(cuisine)
        self.lowRatedRecipe.dietary_tags.add(dietary)
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, {'cuisine_tags': 'Mexican', 'dietary_tags': 'Gluten-Free'})
        context_data = response.context['recipe_data']
        self.assertEqual(len(context_data), 1)
        self.assertEqual(context_data[0]['recipe'].recipe_name, 'Vanilla Cupcakes')