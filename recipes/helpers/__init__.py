"""Helper modules for the recipes app."""
from recipes.helpers.recipe_form import *


def build_recipe_list(recipes, favourite_ids):
    """
    Build a list of recipe dicts with favourite status included.

    Args:
        recipes: Iterable of Recipe objects.
        favourite_ids: Set of recipe IDs the user has favourited.

    Returns:
        List of dicts with 'recipe' and 'is_favourite' keys.
    """
    return [
        {'recipe': r, 'is_favourite': r.id in favourite_ids}
        for r in recipes
    ]
