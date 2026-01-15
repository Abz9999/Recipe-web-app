from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from recipes.models import User


@login_required
def follow_user(request, user_id):
    """Follow another user."""
    user_to_follow = get_object_or_404(User, id=user_id)

    if request.user == user_to_follow:
        messages.error(request, "You cannot follow yourself.")
    elif request.user.is_following(user_to_follow):
        messages.info(request, f"You are already following {user_to_follow.username}")
    else:
        request.user.follow(user_to_follow)
        messages.success(request, f"You are now following {user_to_follow.username}")
    return redirect('user_profile', user_id=user_id)


@login_required
def unfollow_user(request, user_id):
    """Unfollow another user."""
    user_to_unfollow = get_object_or_404(User, id=user_id)

    if request.user == user_to_unfollow:
        messages.error(request, "You cannot unfollow yourself.")
    elif not request.user.is_following(user_to_unfollow):
        messages.info(request, f"You are not following {user_to_unfollow.username}")
    else:
        request.user.unfollow(user_to_unfollow)
        messages.success(request, f"You have unfollowed {user_to_unfollow.username}")
    return redirect('user_profile', user_id=user_id)
