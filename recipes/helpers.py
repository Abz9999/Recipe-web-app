def build_recipe_list(recipes, favourite_ids):
    """Build list of recipe data with favourite status."""
    return [
        {'recipe': r, 'is_favourite': r.id in favourite_ids}
        for r in recipes
    ]
