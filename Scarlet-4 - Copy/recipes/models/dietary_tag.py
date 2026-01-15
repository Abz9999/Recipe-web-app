from django.db import models


class DietaryTag(models.Model):
    """Model for dietary requirement tags"""

    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        """Return the tag name."""
        return self.name
