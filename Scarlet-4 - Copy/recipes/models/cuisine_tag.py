from django.db import models


class CuisineTag(models.Model):
    """Model for cuisine type tags"""

    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        """Return the tag name."""
        return self.name
