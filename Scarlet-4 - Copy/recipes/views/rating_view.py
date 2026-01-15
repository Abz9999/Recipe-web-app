from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, get_object_or_404
from recipes.forms import RatingForm
from recipes.models import Recipe, Rating


@login_required
def rate_recipe(request, pk):
    """Handle recipe rating submissions."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    recipe = get_object_or_404(Recipe, pk=pk)
    existing_rating = Rating.objects.filter(user=request.user, recipe=recipe).first()

    form = RatingForm(request.POST, instance=existing_rating)
    if form.is_valid():
        rating = form.save(commit=False)
        rating.recipe = recipe
        rating.user = request.user
        rating.save()
        action = "updated" if existing_rating else "submitted"
        messages.success(request, f'Your rating has been successfully {action}')
    else:
        messages.error(request, "Invalid rating submission. Please try again!")

    return redirect('recipe', recipe_id=pk)
