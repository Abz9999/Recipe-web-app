"""Unit tests for CuisineTagForm and DietaryTagForm."""
from django.test import TestCase
from recipes.forms import CuisineTagForm, DietaryTagForm


class CuisineTagFormTestCase(TestCase):

    def test_form_accepts_empty_input(self):
        form = CuisineTagForm(data={'cuisine_tags': ''})
        self.assertTrue(form.is_valid())

    def test_form_accepts_single_tag(self):
        form = CuisineTagForm(data={'cuisine_tags': 'Italian'})
        self.assertTrue(form.is_valid())

    def test_form_accepts_multiple_tags(self):
        form = CuisineTagForm(data={'cuisine_tags': 'Italian, Mexican, Thai'})
        self.assertTrue(form.is_valid())

    def test_get_cuisine_tag_names_returns_empty_for_unbound_form(self):
        form = CuisineTagForm()
        self.assertEqual(form.get_cuisine_tag_names(), [])

    def test_get_cuisine_tag_names_returns_empty_for_empty_input(self):
        form = CuisineTagForm(data={'cuisine_tags': ''})
        form.is_valid()
        self.assertEqual(form.get_cuisine_tag_names(), [])

    def test_get_cuisine_tag_names_parses_single_tag(self):
        form = CuisineTagForm(data={'cuisine_tags': 'Italian'})
        form.is_valid()
        self.assertEqual(form.get_cuisine_tag_names(), ['Italian'])

    def test_get_cuisine_tag_names_parses_multiple_tags(self):
        form = CuisineTagForm(data={'cuisine_tags': 'Italian, Mexican, Thai'})
        form.is_valid()
        self.assertEqual(form.get_cuisine_tag_names(), ['Italian', 'Mexican', 'Thai'])

    def test_get_cuisine_tag_names_strips_whitespace(self):
        form = CuisineTagForm(data={'cuisine_tags': '  Italian  ,  Mexican  '})
        form.is_valid()
        self.assertEqual(form.get_cuisine_tag_names(), ['Italian', 'Mexican'])


class DietaryTagFormTestCase(TestCase):

    def test_form_accepts_empty_input(self):
        form = DietaryTagForm(data={'dietary_tags': ''})
        self.assertTrue(form.is_valid())

    def test_form_accepts_single_tag(self):
        form = DietaryTagForm(data={'dietary_tags': 'Vegan'})
        self.assertTrue(form.is_valid())

    def test_form_accepts_multiple_tags(self):
        form = DietaryTagForm(data={'dietary_tags': 'Vegan, Vegetarian, Gluten-Free'})
        self.assertTrue(form.is_valid())

    def test_get_dietary_tag_names_returns_empty_for_unbound_form(self):
        form = DietaryTagForm()
        self.assertEqual(form.get_dietary_tag_names(), [])

    def test_get_dietary_tag_names_returns_empty_for_empty_input(self):
        form = DietaryTagForm(data={'dietary_tags': ''})
        form.is_valid()
        self.assertEqual(form.get_dietary_tag_names(), [])

    def test_get_dietary_tag_names_parses_single_tag(self):
        form = DietaryTagForm(data={'dietary_tags': 'Vegan'})
        form.is_valid()
        self.assertEqual(form.get_dietary_tag_names(), ['Vegan'])

    def test_get_dietary_tag_names_parses_multiple_tags(self):
        form = DietaryTagForm(data={'dietary_tags': 'Vegan, Vegetarian, Gluten-Free'})
        form.is_valid()
        self.assertEqual(form.get_dietary_tag_names(), ['Vegan', 'Vegetarian', 'Gluten-Free'])

    def test_get_dietary_tag_names_strips_whitespace(self):
        form = DietaryTagForm(data={'dietary_tags': '  Vegan  ,  Vegetarian  '})
        form.is_valid()
        self.assertEqual(form.get_dietary_tag_names(), ['Vegan', 'Vegetarian'])
