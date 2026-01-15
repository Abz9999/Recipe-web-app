from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from recipes.views.decorators import author_required


@login_required
@author_required
def delete_recipe(request, recipe_id, recipe=None):
    """Delete a recipe. Only accessible via POST by the recipe author."""
    if request.method == 'POST':
        recipe_name = recipe.recipe_name
        recipe.delete()
        messages.success(request, f'Recipe "{recipe_name}" has been deleted.')
        return redirect('welcome')
    return redirect('recipe', recipe_id=recipe_id)
