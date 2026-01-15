from django.db import models
from django.contrib.auth import get_user_model
from .recipe import Recipe

User = get_user_model()


class Comment(models.Model):
    """Model representing a user comment on a recipe."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        """Return string representation of the comment."""
        return f"Comment by {self.author} on {self.recipe}"