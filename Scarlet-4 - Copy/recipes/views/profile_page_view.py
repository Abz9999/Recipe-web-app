from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from recipes.helpers import build_recipe_list
from recipes.models import Recipe


@login_required
def profile_page_view(request):
    """Display the logged-in user's profile with tabbed sections."""
    user = request.user
    tab = request.GET.get('tab', 'account')
    user_recipes = Recipe.objects.filter(author=user).order_by('-publication_date')
    favourites = user.get_favourites().order_by('-publication_date')

    recipes_page_obj = paginate(user_recipes, request, 'recipes_page')
    favourites_page_obj = paginate(favourites, request, 'favourites_page')

    favourite_ids = set(user.get_favourites().values_list('id', flat=True))
    recipes_with_fav = build_recipe_list(recipes_page_obj, favourite_ids)

    context = build_profile_context(
        user, tab, user_recipes, recipes_page_obj, recipes_with_fav,
        favourites, favourites_page_obj
    )
    return render(request, 'profile_page.html', context)


def paginate(queryset, request, page_param):
    """Paginate a queryset using the given page parameter."""
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get(page_param, 1)
    return paginator.get_page(page_number)


def build_profile_context(user, tab, user_recipes, recipes_page_obj, recipes_with_fav, favourites, favourites_page_obj):
    """Build the context dict for the profile page."""
    return {
        'profile_user': user, 'selected_tab': tab, 'is_own_profile': True,
        'followers': user.get_followers(), 'following': user.get_following(),
        'user_recipes': user_recipes, 'recipes_page_obj': recipes_page_obj,
        'recipes_with_fav': recipes_with_fav, 'favourites_page_obj': favourites_page_obj,
        'followers_count': user.get_followers_count(), 'following_count': user.get_following_count(),
        'recipes_count': user_recipes.count(), 'favourites': favourites,
        'favourites_count': user.get_favourites_count(),
    }
