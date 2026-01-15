from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from recipes.forms import CuisineTagForm, DietaryTagForm, RatingForm
from recipes.models import CuisineTag, DietaryTag, Rating, Recipe


def welcome(request):
    """Display the welcome page with filtered, sorted, paginated recipes."""
    params = extract_request_params(request)
    recipes = get_filtered_recipes(params, request.user)
    recipe_data = sort_recipes(build_recipe_data(recipes, request.user), params['sort'])
    page_obj = paginate_recipes(recipe_data, request)
    context = build_welcome_context(params, page_obj, request)
    return render(request, 'welcome.html', context)


def extract_request_params(request):
    """Extract search and filter parameters from request."""
    return {
        'q': request.GET.get('q', ''),
        'sort': request.GET.get('sort'),
        'filter': request.GET.get('filter'),
        'cuisine_tags': request.GET.get('cuisine_tags', ''),
        'dietary_tags': request.GET.get('dietary_tags', ''),
    }


def build_welcome_context(params, page_obj, request):
    """Build context for the welcome page."""
    return {
        'recipe_data': page_obj, 'page_obj': page_obj,
        'page_url_prefix': build_page_url_prefix(request),
        'cuisine_tag_form': CuisineTagForm(initial={'cuisine_tags': params['cuisine_tags']}),
        'dietary_tag_form': DietaryTagForm(initial={'dietary_tags': params['dietary_tags']}),
    }


def extract_comma_separated_tags(tags_string):
    """Split a comma-separated string into a list of cleaned tag names."""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]


def paginate_recipes(recipe_data, request):
    """Paginate recipe data, 12 per page."""
    paginator = Paginator(recipe_data, 12)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def build_page_url_prefix(request):
    """Build the URL prefix for pagination links, preserving other params."""
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_string = query_params.urlencode()
    return f'?{query_string}&page=' if query_string else '?page='


def apply_query_filter(recipes, query):
    """Filter recipes by search query."""
    if not query:
        return recipes
    return recipes.filter(
        Q(recipe_name__icontains=query) |
        Q(author__username__icontains=query) |
        Q(author__first_name__icontains=query) |
        Q(author__last_name__icontains=query) |
        Q(recipeingredient__name__icontains=query) |
        Q(description__icontains=query)
    ).distinct()


def apply_tag_filter(recipes, cuisine_tag_names, dietary_tag_names):
    """Filter recipes by cuisine and/or dietary tags."""
    if not cuisine_tag_names and not dietary_tag_names:
        return recipes

    recipes = apply_cuisine_filter(recipes, cuisine_tag_names)
    recipes = apply_dietary_filter(recipes, dietary_tag_names)
    return recipes


def apply_cuisine_filter(recipes, tag_names):
    """Filter recipes by cuisine tags."""
    if not tag_names:
        return recipes
    matching_tags = get_matching_cuisine_tags(tag_names)
    if not matching_tags:
        return recipes.none()
    return recipes.filter(cuisine_tags__in=matching_tags).distinct()


def apply_dietary_filter(recipes, tag_names):
    """Filter recipes by dietary tags."""
    if not tag_names:
        return recipes
    matching_tags = get_matching_dietary_tags(tag_names)
    if not matching_tags:
        return recipes.none()
    return recipes.filter(dietary_tags__in=matching_tags).distinct()


def get_matching_cuisine_tags(tag_names):
    """Find cuisine tags matching the given names."""
    all_tags = CuisineTag.objects.all()
    lower_names = [name.strip().lower() for name in tag_names]
    return [tag for tag in all_tags if tag.name.lower() in lower_names]


def get_matching_dietary_tags(tag_names):
    """Find dietary tags matching the given names."""
    all_tags = DietaryTag.objects.all()
    lower_names = [name.strip().lower() for name in tag_names]
    return [tag for tag in all_tags if tag.name.lower() in lower_names]


def apply_following_filter(recipes, filter_type, user):
    """Filter to show only recipes from users the current user follows."""
    if filter_type == 'following' and user.is_authenticated:
        followed_users = user.get_following()
        return recipes.filter(author__in=followed_users)
    return recipes


def build_recipe_data(recipes, user):
    """Build a list of recipe data dicts with ratings and favourite status."""
    return [build_single_recipe_data(recipe, user) for recipe in recipes]


def build_single_recipe_data(recipe, user):
    """Build the data dict for a single recipe card."""
    avg_rating = recipe.average_rating()
    is_fav = user.has_favourited(recipe) if user.is_authenticated else False
    return {
        'recipe': recipe,
        'stars': build_stars(avg_rating),
        'rating_form': get_rating_form(recipe, user),
        'avg': avg_rating,
        'is_favourite': is_fav,
    }


def build_stars(avg_rating):
    """Convert a rating to a list of star types for display."""
    if avg_rating is None:
        return []
    full = int(avg_rating)
    half = 1 if avg_rating - full >= 0.5 else 0
    empty = 5 - full - half
    return ['full'] * full + ['half'] * half + ['empty'] * empty


def get_rating_form(recipe, user):
    """Get a rating form pre-filled with the user's existing rating if any."""
    if not user.is_authenticated:
        return None
    rating = Rating.objects.filter(recipe=recipe, user=user).first()
    return RatingForm(instance=rating)


def sort_recipes(recipe_data, sort_type):
    """Sort recipes by rating if a sort type is specified."""
    if sort_type == 'highest':
        return sorted(recipe_data, key=rating_key, reverse=True)
    if sort_type == 'lowest':
        return sorted(recipe_data, key=rating_key)
    return recipe_data


def rating_key(item):
    """Get rating value for sorting."""
    return item['avg'] or 0


def get_filtered_recipes(params, user):
    """Apply all filters to get the final recipe queryset."""
    cuisine_tags = extract_comma_separated_tags(params['cuisine_tags'])
    dietary_tags = extract_comma_separated_tags(params['dietary_tags'])
    recipes = Recipe.objects.all()
    recipes = apply_query_filter(recipes, params['q'])
    recipes = apply_tag_filter(recipes, cuisine_tags, dietary_tags)
    recipes = apply_following_filter(recipes, params['filter'], user)
    return recipes