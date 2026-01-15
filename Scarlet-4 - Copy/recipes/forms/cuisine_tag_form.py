"""Form for filtering recipes by cuisine tags."""
from django import forms


class CuisineTagForm(forms.Form):
    """
    Search form for filtering recipes by cuisine type.

    Fields:
        cuisine_tags: Comma-separated list of cuisine names to filter by.
    """

    cuisine_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Italian, Mexican, Thai'
        })
    )

    def get_cuisine_tag_names(self):
        """
        Parse the input into a list of tag names.

        Returns:
            List of cleaned tag name strings.
        """
        if not self.is_valid():
            return []
        tag_string = self.cleaned_data.get('cuisine_tags', '').strip()
        if not tag_string:
            return []
        return [name.strip() for name in tag_string.split(',') if name.strip()]
