from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg


class Recipe(models.Model):
    """
    Model representing a recipe created by a user.

    Includes basic info (name, description, difficulty), instructions,
    an optional image, and relationships to tags and ingredients.
    """

    DIFFICULTY_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        editable=False,
        null=True
    )
    recipe_name = models.CharField(max_length=255)
    publication_date = models.DateField(auto_now_add=True)
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1
    )
    description = models.TextField()
    instructions = models.TextField(
        help_text='Enter each instruction on a new line',
        default=''
    )
    image = models.ImageField(blank=True, upload_to='recipes/')
    dietary_tags = models.ManyToManyField(
        'DietaryTag',
        related_name='recipes',
        blank=True
    )
    cuisine_tags = models.ManyToManyField(
        'CuisineTag',
        related_name='recipes',
        blank=True
    )

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return (
            f"{self.recipe_name} by {self.author} ({self.publication_date}) "
            f"difficulty: {self.difficulty}/5 description: {self.description}"
        )

    def average_rating(self):
        """
        Calculate the average rating for this recipe.

        Returns:
            Float rounded to 2 decimal places, or None if no ratings.
        """
        average = self.ratings.aggregate(Avg('rating'))['rating__avg']
        if average is None:
            return None
        return round(average, 2)
