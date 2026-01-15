"""Mixin for applying Bootstrap styling to form fields."""


class StyledFormMixin:
    """
    Mixin that adds 'form-control' class to all form fields.
    """

    def __init__(self, *args, **kwargs):
        """Initialise form and add form-control classes."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
