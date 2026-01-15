from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from recipes.helpers import build_recipe_list
from recipes.models import User, Recipe


@login_required
def other_user_profile_view(request, user_id):
    """
    Display another user's public profile.

    Shows their recipes, follower/following counts, and allows the
    current user to follow/unfollow them.
    """
    profile_user = get_object_or_404(User, id=user_id)
    user_recipes = Recipe.objects.filter(author=profile_user).order_by('-publication_date')
    page_obj = Paginator(user_recipes, 12).get_page(request.GET.get('page'))
    favourite_ids = set(request.user.get_favourites().values_list('id', flat=True))
    context = build_other_profile_context(profile_user, user_recipes, page_obj, favourite_ids, request)
    return render(request, 'other_user_profile.html', context)


def build_other_profile_context(profile_user, user_recipes, page_obj, favourite_ids, request):
    """Build context for another user's profile page."""
    return {
        'profile_user': profile_user, 'current_user': request.user, 'is_own_profile': False,
        'user_recipes': user_recipes, 'page_obj': page_obj,
        'recipes_with_fav': build_recipe_list(page_obj, favourite_ids),
        'followers': profile_user.get_followers(), 'following': profile_user.get_following(),
        'recipes_count': user_recipes.count(),
        'followers_count': profile_user.get_followers_count(),
        'following_count': profile_user.get_following_count(),
        'is_following': request.user.is_following(profile_user),
    }
