from django.test import TestCase
from recipes.models import CuisineTag, DietaryTag


class CuisineTagModelTestCase(TestCase):
    """Unit tests for the CuisineTag model."""

    def setUp(self):
        self.tag = CuisineTag.objects.create(name='Italian')

    def test_str_returns_name(self):
        self.assertEqual(str(self.tag), 'Italian')

    def test_tags_ordered_by_name(self):
        CuisineTag.objects.create(name='Mexican')
        CuisineTag.objects.create(name='Thai')
        tags = list(CuisineTag.objects.all())
        self.assertEqual(tags[0].name, 'Italian')
        self.assertEqual(tags[1].name, 'Mexican')
        self.assertEqual(tags[2].name, 'Thai')


class DietaryTagModelTestCase(TestCase):
    """Unit tests for the DietaryTag model."""

    def setUp(self):
        self.tag = DietaryTag.objects.create(name='Vegan')

    def test_str_returns_name(self):
        self.assertEqual(str(self.tag), 'Vegan')

    def test_tags_ordered_by_name(self):
        DietaryTag.objects.create(name='Vegetarian')
        DietaryTag.objects.create(name='Gluten-Free')
        tags = list(DietaryTag.objects.all())
        self.assertEqual(tags[0].name, 'Gluten-Free')
        self.assertEqual(tags[1].name, 'Vegan')
        self.assertEqual(tags[2].name, 'Vegetarian')
