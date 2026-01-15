from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from recipes.forms import RecipeForm
from recipes.helpers import (
    combine_instruction_steps,
    ensure_min_list,
    extract_cuisine_tag_data,
    extract_dietary_tag_data,
    extract_form_data,
    extract_ingredient_data,
    extract_instruction_steps,
    find_action_in_post,
    get_empty_cuisine_tag,
    get_empty_dietary_tag,
    get_empty_ingredient,
    get_instruction_steps_from_text,
    save_ingredients_to_recipe,
    save_tags_to_recipe,
)
from recipes.views.decorators import author_required


@login_required
@author_required
def edit_recipe(request, recipe_id, recipe=None):
    """Handle recipe editing with dynamic form fields."""
    if request.method == 'POST':
        return handle_post_request(request, recipe)
    return render_get_request(request, recipe)


def handle_post_request(request, recipe):
    """Process POST: either handle dynamic action or save recipe."""
    ingredients = extract_ingredient_data(request.POST, include_id=True)
    instruction_steps = extract_instruction_steps(request.POST)
    cuisine_tags = extract_cuisine_tag_data(request.POST)
    dietary_tags = extract_dietary_tag_data(request.POST)
    form_data = extract_form_data(request.POST)

    action_result = handle_dynamic_actions(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )
    if action_result:
        return action_result

    return save_recipe(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def handle_dynamic_actions(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags
):
    """Check for and handle add/delete button clicks."""
    result = handle_delete_actions(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )
    if result:
        return result

    return handle_add_actions(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def handle_delete_actions(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags
):
    """Check for delete button clicks and handle them."""
    delete_handlers = [
        ('delete_ingredient_', handle_delete_ingredient),
        ('delete_instruction_', handle_delete_instruction),
        ('delete_cuisine_tag_', handle_delete_cuisine_tag),
        ('delete_dietary_tag_', handle_delete_dietary_tag),
    ]

    for prefix, handler in delete_handlers:
        index = find_action_in_post(request.POST, prefix)
        if index is not None:
            return handler(
                request, recipe, form_data, ingredients, instruction_steps,
                cuisine_tags, dietary_tags, index
            )
    return None


def handle_add_actions(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags
):
    """Check for add button clicks and handle them."""
    add_actions = [
        ('add_ingredient', ingredients, get_empty_ingredient()),
        ('add_instruction', instruction_steps, ''),
        ('add_cuisine_tag', cuisine_tags, ''),
        ('add_dietary_tag', dietary_tags, ''),
    ]

    for action_name, target_list, empty_value in add_actions:
        if action_name in request.POST:
            target_list.append(empty_value)
            return render_edit_form(
                request, recipe, form_data, ingredients, instruction_steps,
                cuisine_tags, dietary_tags
            )
    return None


def handle_delete_ingredient(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags, index
):
    """Remove ingredient at index and re-render form."""
    ingredients = extract_ingredient_data(request.POST, include_id=True)
    if 0 <= index < len(ingredients):
        ingredients.pop(index)
    ingredients = ensure_min_list(ingredients, get_empty_ingredient())
    return render_edit_form(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def handle_delete_instruction(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags, index
):
    """Remove instruction at index and re-render form."""
    if 0 <= index < len(instruction_steps):
        instruction_steps.pop(index)
    instruction_steps = ensure_min_list(instruction_steps)
    return render_edit_form(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def handle_delete_cuisine_tag(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags, index
):
    """Remove cuisine tag at index and re-render form."""
    if 0 <= index < len(cuisine_tags):
        cuisine_tags.pop(index)
    cuisine_tags = ensure_min_list(cuisine_tags)
    return render_edit_form(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def handle_delete_dietary_tag(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags, index
):
    """Remove dietary tag at index and re-render form."""
    if 0 <= index < len(dietary_tags):
        dietary_tags.pop(index)
    dietary_tags = ensure_min_list(dietary_tags)
    return render_edit_form(
        request, recipe, form_data, ingredients, instruction_steps,
        cuisine_tags, dietary_tags
    )


def save_recipe(
    request, recipe, form_data, ingredients, instruction_steps,
    cuisine_tags, dietary_tags
):
    """Validate and save the edited recipe."""
    post_data = request.POST.copy()
    post_data['instructions'] = combine_instruction_steps(instruction_steps)

    form = RecipeForm(post_data, request.FILES, instance=recipe)
    
    ingredient_error = None
    instruction_error = None
    
    if not has_valid_ingredients(ingredients):
        ingredient_error = 'At least one ingredient is required.'
    if not has_valid_instructions(instruction_steps):
        instruction_error = 'At least one instruction is required.'
        if 'instructions' in form.errors:
            form.errors.pop('instructions', None)
    
    if not form.is_valid() or ingredient_error or instruction_error:
        return render_edit_form(
            request, recipe, form_data, ingredients, instruction_steps,
            cuisine_tags, dietary_tags, form=form,
            ingredient_error=ingredient_error, instruction_error=instruction_error
        )

    recipe = form.save()
    save_ingredients_to_recipe(recipe, ingredients)
    save_tags_to_recipe(recipe, cuisine_tags, dietary_tags)
    return HttpResponseRedirect(reverse('recipe', kwargs={'recipe_id': recipe.id}))


def has_valid_ingredients(ingredients):
    """Check if at least one ingredient has a non-empty name."""
    return any(ing.get('name', '').strip() for ing in ingredients)


def has_valid_instructions(instruction_steps):
    """Check if at least one instruction step has non-empty content."""
    return any(step.strip() for step in instruction_steps)


def render_get_request(request, recipe):
    """Render the edit form pre-filled with existing recipe data."""
    return render(request, 'edit_recipe.html', {
        'form': RecipeForm(instance=recipe), 'recipe': recipe,
        'ingredients': get_existing_ingredients(recipe),
        'instruction_steps': get_instruction_steps_from_text(recipe.instructions),
        'cuisine_tags': get_existing_cuisine_tags(recipe),
        'dietary_tags': get_existing_dietary_tags(recipe),
    })


def render_edit_form(request, recipe, form_data, ingredients, instruction_steps, cuisine_tags, dietary_tags, form=None, ingredient_error=None, instruction_error=None):
    """Render the recipe edit form with current field values."""
    if form is None:
        form = RecipeForm(initial=form_data, instance=recipe)
    return render(request, 'edit_recipe.html', {
        'form': form, 'recipe': recipe, 'ingredients': ingredients,
        'instruction_steps': instruction_steps, 'cuisine_tags': cuisine_tags, 'dietary_tags': dietary_tags,
        'ingredient_error': ingredient_error, 'instruction_error': instruction_error,
    })


def get_existing_ingredients(recipe):
    """Get recipe's current ingredients as a list of dicts."""
    ingredients = [ingredient_to_dict(ing) for ing in recipe.recipeingredient_set.all()]
    return ingredients if ingredients else [get_empty_ingredient()]


def ingredient_to_dict(ing):
    """Convert an ingredient model to a dict."""
    return {'id': str(ing.id), 'name': ing.name, 'amount': str(ing.amount) if ing.amount else '', 'units': ing.units}


def get_existing_cuisine_tags(recipe):
    """Get recipe's current cuisine tags as a list of names."""
    tags = [tag.name for tag in recipe.cuisine_tags.all()]
    return tags if tags else [get_empty_cuisine_tag()]


def get_existing_dietary_tags(recipe):
    """Get recipe's current dietary tags as a list of names."""
    tags = [tag.name for tag in recipe.dietary_tags.all()]
    return tags if tags else [get_empty_dietary_tag()]