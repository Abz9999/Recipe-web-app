from django import forms 
from django.test import TestCase
from recipes.forms import RatingForm
from recipes.models import User, Recipe, Rating

class RatingFormTestCase(TestCase):

    fixtures = [
        'recipes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.recipe = Recipe.objects.create(
            author=self.user,
            recipe_name='Chocolate Cake',
            difficulty = 3,
            description="Easy to make and sweet"
        )

        self.form_input = {
            'rating': 4,
        }

    def test_form_has_necessary_fields(self):
        form = RatingForm()
        self.assertIn('rating', form.fields)
        rating_field = form.fields['rating']
        self.assertIsInstance(rating_field, forms.ChoiceField)
        self.assertNotIn('user', form.fields)
        self.assertNotIn('recipe', form.fields)
        self.assertNotIn('created_at', form.fields)

    def test_form_is_valid_with_all_data(self):
        form = RatingForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_rating_cannot_be_blank(self):
        self.form_input['rating'] = ''
        form = RatingForm(data = self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
    
    def test_rating_cannot_be_greater_than_5(self):
        self.form_input['rating'] = 6
        form = RatingForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_rating_cannot_be_less_than_1(self):
        self.form_input['rating'] = 0
        form = RatingForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = RatingForm(data = self.form_input)
        before_count = Rating.objects.count()
        self.assertTrue(form.is_valid())
        rating_instance = form.save(commit = False)
        rating_instance.user = self.user
        rating_instance.recipe = self.recipe
        rating_instance.save()
        after_count = Rating.objects.count()
        self.assertEqual(before_count+1, after_count)

