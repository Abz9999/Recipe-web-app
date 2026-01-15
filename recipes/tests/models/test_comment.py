"""Unit tests for the Comment model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipes.models import User, Recipe, Comment


class CommentModelTestCase(TestCase):
    """Unit tests for the Comment model."""

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
        self.comment = Comment.objects.create(
            recipe=self.recipe,
            author=self.user,
            text='This is a test comment'
        )

    def test_valid_comment(self):
        self.assert_comment_is_valid()

    def test_text_cannot_be_blank(self):
        self.comment.text = ''
        self.assert_comment_is_invalid()

    def test_text_can_be_long(self):
        self.comment.text = 'x' * 1000
        self.assert_comment_is_valid()

    def test_comment_has_timestamp(self):
        self.assertIsNotNone(self.comment.timestamp)

    def test_str_method(self):
        self.assertIn('johndoe', str(self.comment))
        self.assertIn('Chocolate Cake', str(self.comment))

    def test_comment_is_deleted_when_recipe_is_deleted(self):
        self.recipe.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_is_deleted_when_author_is_deleted(self):
        self.user.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def assert_comment_is_valid(self):
        try:
            self.comment.full_clean()
        except ValidationError:
            self.fail('Test comment should be valid')

    def assert_comment_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.comment.full_clean()
