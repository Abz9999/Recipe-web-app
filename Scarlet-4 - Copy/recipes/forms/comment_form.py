"""Form for submitting comments on recipes."""
from django import forms
from recipes.models import Comment


class CommentForm(forms.ModelForm):
    """
    Form for users to post comments on recipes.

    Fields:
        text: The comment content (multi-line text area).
    """

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Write a comment...',
            })
        }
