from django.core.validators import MinValueValidator
from django.db import models


class RecipeIngredient(models.Model):
    """Model representing an ingredient in a recipe."""

    UNIT_CHOICES = [
        ('ml', 'ml'),
        ('g', 'g'),
        ('L', 'L'),
        ('kg', 'kg'),
        ('oz', 'oz'),
    ]

    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    amount = models.IntegerField(validators = [MinValueValidator(1)], default=1)
    units = models.CharField(max_length=10, choices=UNIT_CHOICES, default='g')

    class Meta:
        ordering = ['id']

    def __str__(self):
        """Return string representation of the ingredient."""
        return f"{self.amount}{self.units} {self.name}"
