from django.test import TestCase
from django.urls import reverse
from recipes.models import User, Recipe, Comment, RecipeIngredient, Rating, CuisineTag
from recipes.models.favourite import Favourite


class RecipeViewTestCase(TestCase):
    """Tests of the recipe view."""

    fixtures = ['recipes/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.create_user(
            username='@janedoe',
            email='jane@example.com',
            password='Password123'
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Test Recipe',
            difficulty=3,
            description='Test description',
            instructions='Step 1\nStep 2'
        )
        RecipeIngredient.objects.create(recipe=self.recipe, name='Ingredient 1', amount=100, units='g')
        RecipeIngredient.objects.create(recipe=self.recipe, name='Ingredient 2', amount=200, units='g')
        self.url = reverse('recipe', kwargs={'recipe_id': self.recipe.id})

    def test_recipe_url(self):
        self.assertEqual(self.url, f'/recipes/{self.recipe.id}/')

    def test_get_recipe_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_recipe_when_logged_in(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe.html')

    def test_nonexistent_recipe_shows_not_found(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse('recipe', kwargs={'recipe_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recipe not found')

    def test_recipe_displays_recipe_name(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_displays_description(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Test description')

    def test_recipe_displays_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Ingredient 1')
        self.assertContains(response, 'Ingredient 2')

    def test_recipe_displays_instructions(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Step 1')
        self.assertContains(response, 'Step 2')

    def test_recipe_displays_difficulty(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '3/5')

    def test_recipe_displays_author_username(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '@johndoe')

    def test_recipe_displays_tags(self):
        tag = CuisineTag.objects.create(name='Italian')
        self.recipe.cuisine_tags.add(tag)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Italian')

    def test_post_comment(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, {'text': 'This is a test comment'})
        self.assertRedirects(response, self.url)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'This is a test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.recipe, self.recipe)

    def test_empty_comment_not_saved(self):
        self.client.login(username='@johndoe', password='Password123')
        self.client.post(self.url, {'text': ''})
        self.assertEqual(Comment.objects.count(), 0)

    def test_comments_displayed(self):
        Comment.objects.create(recipe=self.recipe, author=self.user, text='Existing comment')
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Existing comment')

    def test_multiple_comments(self):
        Comment.objects.create(recipe=self.recipe, author=self.user, text='Comment 1')
        Comment.objects.create(recipe=self.recipe, author=self.other_user, text='Comment 2')
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Comment 1')
        self.assertContains(response, 'Comment 2')

    def test_submit_rating(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, {'rating': 4, 'submit_rating': True})
        self.assertRedirects(response, self.url)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().rating, 4)

    def test_update_rating(self):
        Rating.objects.create(user=self.user, recipe=self.recipe, rating=3)
        self.client.login(username='@johndoe', password='Password123')
        self.client.post(self.url, {'rating': 5, 'submit_rating': True})
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().rating, 5)

    def test_average_rating_displayed(self):
        Rating.objects.create(user=self.user, recipe=self.recipe, rating=4)
        Rating.objects.create(user=self.other_user, recipe=self.recipe, rating=2)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '3')

    def test_user_rating_in_context(self):
        Rating.objects.create(user=self.user, recipe=self.recipe, rating=4)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['user_rating'].rating, 4)

    def test_no_ratings_message(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'No ratings')

    def test_unfavourited_recipe(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertFalse(response.context['has_favourited'])
        self.assertContains(response, 'bi-heart')

    def test_favourited_recipe(self):
        Favourite.objects.create(user=self.user, recipe=self.recipe)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertTrue(response.context['has_favourited'])
        self.assertContains(response, 'bi-heart-fill')

    def test_favourite_url_present(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, reverse('favourite_recipe', kwargs={'recipe_id': self.recipe.id}))

    def test_unfavourite_url_when_favourited(self):
        Favourite.objects.create(user=self.user, recipe=self.recipe)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, reverse('unfavourite_recipe', kwargs={'recipe_id': self.recipe.id}))

    def test_author_sees_edit_button(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id}))
        self.assertContains(response, 'Edit Recipe')

    def test_author_sees_delete_button(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Delete Recipe')

    def test_non_author_cannot_see_edit(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertNotContains(response, reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id}))

    def test_non_author_cannot_see_delete(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Delete Recipe')

    def test_context_has_required_keys(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        for key in ['recipe', 'comments', 'ingredients_list', 'instructions_list', 
                    'form', 'rating_form', 'avg_rating', 'total_ratings', 'has_favourited']:
            self.assertIn(key, response.context)

    def test_ingredients_list_correct(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['ingredients_list']), 2)

    def test_instructions_parsed_correctly(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['instructions_list'], ['Step 1', 'Step 2'])

    def test_recipe_with_no_instructions(self):
        self.recipe.instructions = ''
        self.recipe.save()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['instructions_list'], [])

    def test_recipe_with_no_ingredients(self):
        RecipeIngredient.objects.filter(recipe=self.recipe).delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['ingredients_list']), 0)

    def test_total_ratings_count(self):
        Rating.objects.create(user=self.user, recipe=self.recipe, rating=4)
        Rating.objects.create(user=self.other_user, recipe=self.recipe, rating=3)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['total_ratings'], 2)

    def test_avg_rating_rounded(self):
        Rating.objects.create(user=self.user, recipe=self.recipe, rating=4)
        Rating.objects.create(user=self.other_user, recipe=self.recipe, rating=3)
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['avg_rating'], 3.5)

    def test_comments_ordered_newest_first(self):
        c1 = Comment.objects.create(recipe=self.recipe, author=self.user, text='First')
        c2 = Comment.objects.create(recipe=self.recipe, author=self.user, text='Second')
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        comments = list(response.context['comments'])
        self.assertEqual(comments[0].id, c2.id)
        self.assertEqual(comments[1].id, c1.id)

    def test_invalid_rating_not_saved(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, {'rating': 10, 'submit_rating': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rating.objects.count(), 0)

    def test_user_rating_none_when_not_rated(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertIsNone(response.context['user_rating'])

    def test_avg_rating_none_when_no_ratings(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertIsNone(response.context['avg_rating'])

    def test_servings_scales_ingredients(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url + '?servings=2')
        ingredients = response.context['ingredients_list']
        self.assertEqual(ingredients[0]['amount'], 200)
        self.assertEqual(ingredients[1]['amount'], 400)

    def test_invalid_servings_uses_default(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url + '?servings=invalid')
        self.assertEqual(response.context['servings'], 1)

    def test_comment_keeps_servings_param(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url + '?servings=3', {'text': 'Test comment'})
        self.assertRedirects(response, self.url + '?servings=3')

    def test_rating_keeps_servings_param(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url + '?servings=2', {'rating': 4, 'submit_rating': True})
        self.assertRedirects(response, self.url + '?servings=2')