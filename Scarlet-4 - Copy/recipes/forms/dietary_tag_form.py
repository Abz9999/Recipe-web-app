"""Form for filtering recipes by dietary tags."""
from django import forms


class DietaryTagForm(forms.Form):
    """
    Search form for filtering recipes by dietary requirements.

    Fields:
        dietary_tags: Comma-separated list of dietary tags to filter by.
    """

    dietary_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Vegan, Vegetarian, Gluten-Free'
        })
    )

    def get_dietary_tag_names(self):
        """
        Parse the input into a list of tag names.

        Returns:
            List of cleaned tag name strings.
        """
        if not self.is_valid():
            return []
        tag_string = self.cleaned_data.get('dietary_tags', '').strip()
        if not tag_string:
            return []
        return [name.strip() for name in tag_string.split(',') if name.strip()]
