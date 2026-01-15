from django.contrib.auth import get_user_model
from django.db import models
from .recipe import Recipe

User = get_user_model()


class Favourite(models.Model):
    """Model representing a user's favourite recipe."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-created_at']

    def __str__(self):
        """Return string representation of the favourite."""
        return f"{self.user.username} favourited {self.recipe.recipe_name}"
