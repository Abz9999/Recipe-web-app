from django import forms
from django.test import TestCase
from recipes.forms import CommentForm


class CommentFormTestCase(TestCase):
    """Unit tests of the comment form."""

    def setUp(self):
        self.form_input = {'text': 'This is a test comment'}

    def test_form_contains_required_fields(self):
        form = CommentForm()
        self.assertIn('text', form.fields)

    def test_text_field_is_textarea(self):
        form = CommentForm()
        text_field = form.fields['text']
        self.assertTrue(isinstance(text_field.widget, forms.Textarea))

    def test_form_accepts_valid_input(self):
        form = CommentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_text(self):
        self.form_input['text'] = ''
        form = CommentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_long_text(self):
        self.form_input['text'] = 'x' * 1000
        form = CommentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

