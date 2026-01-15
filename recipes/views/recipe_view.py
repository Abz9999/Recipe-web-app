from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from recipes.forms import CommentForm, RatingForm
from recipes.models import Recipe, Comment, Rating


@login_required
def recipe_view(request, recipe_id):
    """Display a recipe with its comments and ratings."""
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        return render(request, 'recipe.html', get_not_found_context())

    user_rating = Rating.objects.filter(user=request.user, recipe=recipe).first()
    forms_result = get_forms_for_request(request, recipe, user_rating)

    if isinstance(forms_result, HttpResponseRedirect):
        return forms_result

    comment_form, rating_form = forms_result
    context = build_context(recipe, comment_form, rating_form, user_rating, request)
    return render(request, 'recipe.html', context)


def get_recipe_data(recipe, servings=1):
    """Get ingredients and instructions, adjusting amounts for servings."""
    ingredients_list = recipe.recipeingredient_set.all()
    instructions = recipe.instructions.splitlines() if recipe.instructions else []
    adjusted_ingredients = [adjust_ingredient(ing, servings) for ing in ingredients_list]
    return adjusted_ingredients, instructions


def adjust_ingredient(ingredient, servings):
    """Adjust ingredient amount for the given number of servings."""
    adjusted_amount = round(ingredient.amount * servings * 10) / 10
    return {
        'name': ingredient.name,
        'amount': adjusted_amount,
        'units': ingredient.units,
        'base_amount': ingredient.amount,
    }


def get_rating_data(recipe):
    """Calculate average rating and total count for a recipe."""
    avg_rating = Rating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else None
    total_ratings = Rating.objects.filter(recipe=recipe).count()
    return avg_rating, total_ratings


def handle_rating_submission(request, recipe, user_rating):
    """Process a rating form submission."""
    rating_form = RatingForm(request.POST, instance=user_rating)
    if not rating_form.is_valid():
        return None, rating_form, CommentForm()

    rating = rating_form.save(commit=False)
    rating.recipe = recipe
    rating.user = request.user
    rating.save()
    return build_redirect(request, recipe), None, None


def handle_comment_submission(request, recipe):
    """Process a comment form submission."""
    comment_form = CommentForm(request.POST)
    if not comment_form.is_valid():
        return None, comment_form, RatingForm()

    comment = comment_form.save(commit=False)
    comment.recipe = recipe
    comment.author = request.user
    comment.save()
    return build_redirect(request, recipe), None, None


def build_redirect(request, recipe):
    """Build redirect URL, preserving the servings parameter if present."""
    servings = request.GET.get('servings', '')
    url = reverse('recipe', kwargs={'recipe_id': recipe.id})
    if servings:
        return redirect(f'{url}?servings={servings}')
    return redirect(url)


def handle_post_request(request, recipe, user_rating):
    """Route POST to the appropriate handler based on which form was submitted."""
    if 'submit_rating' in request.POST:
        return handle_rating_submission(request, recipe, user_rating)
    return handle_comment_submission(request, recipe)


def get_not_found_context():
    """Return context dict for when recipe doesn't exist."""
    return {
        'recipe': None,
        'instructions_list': [],
        'comments': [],
        'form': None,
    }


def get_comments(recipe):
    """Get all comments for a recipe, newest first."""
    return Comment.objects.filter(recipe=recipe).order_by('-timestamp', '-id')


def build_context(recipe, comment_form, rating_form, user_rating, request):
    """Build the full context dict for the recipe template."""
    servings = get_servings_from_request(request)
    ingredients_list, instructions_list = get_recipe_data(recipe, servings)
    avg_rating, total_ratings = get_rating_data(recipe)
    has_fav = request.user.has_favourited(recipe) if request.user.is_authenticated else False
    return {
        'recipe': recipe, 'comments': get_comments(recipe), 'ingredients_list': ingredients_list,
        'form': comment_form, 'rating_form': rating_form, 'user_rating': user_rating,
        'avg_rating': avg_rating, 'total_ratings': total_ratings,
        'instructions_list': instructions_list, 'has_favourited': has_fav, 'servings': servings,
    }


def get_servings_from_request(request):
    """Parse servings from query string, defaulting to 1."""
    try:
        servings = int(request.GET.get('servings', 1))
        return max(1, servings)
    except (ValueError, TypeError):
        return 1


def get_forms_for_request(request, recipe, user_rating):
    """Get the appropriate forms for the request."""
    if request.method != 'POST':
        return CommentForm(), RatingForm(instance=user_rating)

    redirect_response, comment_form, rating_form = handle_post_request(
        request, recipe, user_rating
    )
    if redirect_response:
        return redirect_response

    comment_form = comment_form or CommentForm()
    rating_form = rating_form or RatingForm(instance=user_rating)
    return comment_form, rating_form
