"""Helpers for parsing and saving recipe form data."""
from recipes.models import CuisineTag, DietaryTag, RecipeIngredient

def build_ingredient_dict(post_data, index, include_id):
    """Build a single ingredient dict from POST data."""
    name = post_data.get(f'ingredient_name_{index}', '')
    amount = post_data.get(f'ingredient_amount_{index}', '')
    units = post_data.get(f'ingredient_units_{index}', '')
    
    ingredient = {'name': name, 'amount': amount, 'units': units}
    
    if include_id:
        ingredient['id'] = post_data.get(f'ingredient_id_{index}', '')
    
    return ingredient

def extract_ingredients_loop(post_data, include_id):
    """Extract all ingredients from POST data."""
    ingredients = []
    index = 0
    
    while f'ingredient_name_{index}' in post_data:
        ingredient = build_ingredient_dict(post_data, index, include_id)
        ingredients.append(ingredient)
        index += 1
    
    return ingredients

def extract_ingredient_data(post_data, include_id=False):
    """Pull ingredient data from POST into a list of dicts."""
    ingredients = extract_ingredients_loop(post_data, include_id)
    
    if not ingredients:
        return [get_empty_ingredient()]
    return ingredients

def get_empty_ingredient():
    """Return an empty ingredient dict for initialising forms."""
    return {'name': '', 'amount': '', 'units': ''}

def extract_steps_loop(post_data, prefix):
    """Extract all steps from POST data using the given prefix."""
    steps = []
    index = 0
    
    while f'{prefix}_{index}' in post_data:
        step = post_data.get(f'{prefix}_{index}', '')
        steps.append(step)
        index += 1
    
    return steps

def extract_instruction_steps(post_data):
    """Pull instruction steps from POST into a list."""
    steps = extract_steps_loop(post_data, 'instruction_step')
    
    if not steps:
        return ['']
    return steps

def get_instruction_steps_from_text(instructions_text):
    """Split stored instructions text into separate steps."""
    if not instructions_text:
        return ['']
    
    lines = instructions_text.split('\n')
    steps = [line.strip() for line in lines if line.strip()]
    
    if not steps:
        return ['']
    return steps

def combine_instruction_steps(instruction_steps):
    """Join instruction steps into a single newline-separated string."""
    return '\n'.join(step.strip() for step in instruction_steps if step.strip())

def extract_form_data(post_data):
    """Extract the main recipe form fields from POST data."""
    return {
        'recipe_name': post_data.get('recipe_name', ''),
        'difficulty': post_data.get('difficulty', ''),
        'description': post_data.get('description', ''),
        'instructions': post_data.get('instructions', ''),
    }

def extract_tag_data(post_data, prefix):
    """Pull tag names from POST into a list."""
    tags = extract_steps_loop(post_data, prefix)
    
    if not tags:
        return ['']
    return tags

def extract_cuisine_tag_data(post_data):
    """Pull cuisine tag names from POST into a list."""
    return extract_tag_data(post_data, 'cuisine_tag')

def extract_dietary_tag_data(post_data):
    """Pull dietary tag names from POST into a list."""
    return extract_tag_data(post_data, 'dietary_tag')

def get_empty_cuisine_tag():
    """Return an empty string for a new cuisine tag field."""
    return ''

def get_empty_dietary_tag():
    """Return an empty string for a new dietary tag field."""
    return ''

def find_action_in_post(post_data, prefix):
    """Find which add/delete button was clicked, return its index."""
    for key in post_data:
        if key.startswith(prefix):
            index_str = key.replace(prefix, '')
            return int(index_str)
    return None

def ensure_min_list(items, empty_value=''):
    """Make sure a list has at least one item, adding empty value if needed."""
    if not items:
        return [empty_value]
    return items

def parse_ingredient_amount(amount_str):
    """Parse ingredient amount string to integer, defaulting to 1."""
    if not amount_str:
        return 1
    
    try:
        return int(amount_str)
    except (ValueError, TypeError):
        return 1

def create_ingredient(recipe, ingredient):
    """Create a single RecipeIngredient from a dict."""
    name = ingredient.get('name', '').strip()
    if not name:
        return
    
    amount = parse_ingredient_amount(ingredient.get('amount', ''))
    units = ingredient.get('units', 'g')
    
    RecipeIngredient.objects.create(
        recipe=recipe,
        name=name,
        amount=amount,
        units=units
    )

def save_ingredients_to_recipe(recipe, ingredients):
    """Save ingredients to recipe, replacing existing ones. Skips empty names."""
    RecipeIngredient.objects.filter(recipe=recipe).delete()
    
    for ingredient in ingredients:
        create_ingredient(recipe, ingredient)

def build_tag_objects(tag_names, tag_model):
    """Build tag objects from tag name strings."""
    tag_objects = []
    
    for tag_name in tag_names:
        cleaned_name = tag_name.strip()
        if cleaned_name:
            tag_obj, _ = tag_model.objects.get_or_create(name=cleaned_name)
            tag_objects.append(tag_obj)
    
    return tag_objects

def save_tags_to_recipe(recipe, cuisine_tags, dietary_tags):
    """Save tags to recipe, creating new tag objects if needed."""
    cuisine_objs = build_tag_objects(cuisine_tags, CuisineTag)
    dietary_objs = build_tag_objects(dietary_tags, DietaryTag)
    recipe.cuisine_tags.set(cuisine_objs)
    recipe.dietary_tags.set(dietary_objs)