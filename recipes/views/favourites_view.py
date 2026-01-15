from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from recipes.models import Recipe


@login_required
def favourite_recipe(request, recipe_id):
    """Add a recipe to the current user's favourites."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user.has_favourited(recipe):
        messages.info(request, f"You already favourited {recipe.recipe_name}")
    else:
        request.user.favourite_recipe(recipe)
        messages.success(request, f"Added {recipe.recipe_name} to favourites")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unfavourite_recipe(request, recipe_id):
    """Remove a recipe from the current user's favourites."""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if not request.user.has_favourited(recipe):
        messages.info(request, f"{recipe.recipe_name} is not in your favourites")
    else:
        request.user.unfavourite_recipe(recipe)
        messages.success(request, f"Removed {recipe.recipe_name} from favourites")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def favourites_list(request):
    """Redirect to the profile page with favourites tab selected."""
    return redirect(f'{reverse("profile_page")}?tab=favourites')
