"""Form for creating and editing recipes."""
from django import forms

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    """
    Form for the main recipe details.

    Fields:
        recipe_name: The recipe's title.
        difficulty: Difficulty rating from 1-5.
        description: Brief description of the recipe.
        instructions: Step-by-step cooking instructions.
        image: Optional recipe photo.
    """

    class Meta:
        model = Recipe
        fields = ['recipe_name', 'difficulty', 'description', 'instructions', 'image']
        widgets = {
            'recipe_name': forms.TextInput(attrs={
                'placeholder': 'Enter recipe name',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe your recipe...',
            }),
            'instructions': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': 'Enter cooking instructions...',
            }),
            'image': forms.FileInput(),
        }

    def get_image_filename(self):
        """Return just the filename of the current image."""
        if self.instance and self.instance.image:
            return self.instance.image.name.split('/')[-1]
        return None
