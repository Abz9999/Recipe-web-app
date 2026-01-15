"""Form for rating recipes."""
from django import forms
from recipes.models import Rating


class RatingForm(forms.ModelForm):
    """
    Form for users to rate recipes from 1-5 stars.

    Fields:
        rating: Radio button selection from 1 to 5 stars.
    """

    rating = forms.ChoiceField(
        choices=Rating.RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label=''
    )

    class Meta:
        model = Rating
        fields = ['rating']
