"""
Management command to seed the database with demo data.

This command creates a small set of named fixture users and then fills up
to ``USER_COUNT`` total users using Faker-generated data. Existing records
are left untouched—if a create fails (e.g., due to duplicates), the error
is swallowed and generation continues.
"""

from faker import Faker
from random import randint, choice, sample
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from recipes.models import User, Recipe, RecipeIngredient, Comment, Rating, DietaryTag, CuisineTag, Follow, Favourite

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]


class Command(BaseCommand):
    """
    Build automation command to seed the database with data.

    This command inserts a small set of known users (``user_fixtures``) and then
    repeatedly generates additional random users until ``USER_COUNT`` total users
    exist in the database. Each generated user receives the same default password.

    Attributes:
        USER_COUNT (int): Target total number of users in the database.
        RECIPE_COUNT (int): Target total number of recipes in the database.
        DEFAULT_PASSWORD (str): Default password assigned to all created users.
        help (str): Short description shown in ``manage.py help``.
        faker (Faker): Locale-specific Faker instance used for random data.
    """

    USER_COUNT = 200
    RECIPE_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        """Initialize the command with a locale-specific Faker instance."""
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        """
        Django entrypoint for the command.

        Runs the full seeding workflow and stores ``self.users`` for any
        post-processing or debugging (not required for operation).
        """
        self.create_users()
        self.users = User.objects.all()
        self.create_tags()
        self.create_recipes()
        self.create_ingredients()
        self.create_comments()
        self.create_ratings()
        self.create_follows()
        self.create_favourites()

    def create_users(self):
        """
        Create fixture users and then generate random users up to USER_COUNT.

        The process is idempotent in spirit: attempts that fail (e.g., due to
        uniqueness constraints on username/email) are ignored and generation continues.
        """
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        """Attempt to create each predefined fixture user."""
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        """
        Generate random users until the database contains USER_COUNT users.

        Prints a simple progress indicator to stdout during generation.
        """
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        """
        Generate a single random user and attempt to insert it.

        Uses Faker for first/last names, then derives a simple username/email.
        """
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})

    def try_create_user(self, data):
        """
        Attempt to create a user and ignore any errors.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        """
        Create a user with the default password.

        Args:
            data (dict): Mapping with keys ``username``, ``email``,
                ``first_name``, and ``last_name``.
        """
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_tags(self):
        """Create dietary and cuisine tags."""
        dietary_list = ['Vegan', 'Vegetarian', 'Gluten-Free', 'Dairy-Free', 'Nut-Free', 'Halal', 'Kosher']
        cuisine_list = ['Italian', 'Mexican', 'Chinese', 'Japanese', 'Indian', 'French', 'Thai', 'Mediterranean', 'American', 'British']
        print("Seeding dietary tags...")
        for name in dietary_list:
            DietaryTag.objects.get_or_create(name=name)
        print("Seeding cuisine tags...")
        for name in cuisine_list:
            CuisineTag.objects.get_or_create(name=name)
        print("Tag seeding complete.")

    def create_recipes(self):
        """Create recipes up to RECIPE_COUNT, ensuring fixture users have some."""
        self.create_fixture_recipes()
        all_users = list(User.objects.all())
        recipe_count = Recipe.objects.count()
        while recipe_count < self.RECIPE_COUNT:
            print(f"Seeding recipe {recipe_count}/{self.RECIPE_COUNT}", end='\r')
            author = choice(all_users)
            recipe_name = self.generate_recipe_name()
            self.create_recipe(author, recipe_name)
            recipe_count = Recipe.objects.count()
        print("Recipe seeding complete.      ")

    def generate_recipe_name(self):
        """Generate a recipe name by picking from lists."""
        prefixes = ['Spicy', 'Sweet', 'Creamy', 'Crispy', 'Tender', 'Flavourful', 'Aromatic', 'Savoury', 'Tangy', 'Zesty']
        main_dishes = ['Pasta', 'Rice', 'Soup', 'Salad', 'Stew', 'Curry', 'Stir Fry', 'Roast', 'Bake', 'Grill', 'Cake', 'Pie', 'Bread', 'Chili']
        endings = ['with Chicken', 'and Vegetables', 'with Beef', 'and Herbs', 'with Garlic', 'in Tomato Sauce', 'with Cheese', 'and Mushrooms', 'with Onions', 'and Peppers']
        return f"{choice(prefixes)} {choice(main_dishes)} {choice(endings)}"

    def create_fixture_recipes(self):
        """Create guaranteed recipes for fixture users."""
        fixture_recipes = {
            '@johndoe': ['Chocolate Cake', 'Spaghetti Carbonara', 'Chicken Curry'],
            '@janedoe': ['Vegetable Stir Fry', 'Beef Stew', 'Caesar Salad'],
            '@charlie': ['Fish and Chips', 'Chili Con Carne', 'Pancakes']
        }
        print("Seeding fixture user recipes...")
        for username, recipes in fixture_recipes.items():
            try:
                user = User.objects.get(username=username)
            except:
                continue
            self.add_fixture_recipes_for_user(user, recipes)
    
    def add_fixture_recipes_for_user(self, user, recipes):
        """Add fixture recipes for a specific user."""
        for recipe_name in recipes:
            if Recipe.objects.count() >= self.RECIPE_COUNT:
                return
            if not Recipe.objects.filter(author=user, recipe_name=recipe_name).exists():
                self.create_recipe(user, recipe_name)

    def create_recipe(self, author, recipe_name):
        """Create a single recipe with random data."""
        description = self.faker.text(max_nb_chars=200)
        steps = [self.faker.sentence() for _ in range(randint(3, 8))]
        instructions = '\n'.join(steps)
        difficulty = choice([1, 2, 3, 4, 5])
        
        recipe = Recipe.objects.create(
            author=author, recipe_name=recipe_name, difficulty=difficulty,
            description=description, instructions=instructions
        )
        recipe.publication_date = (timezone.now() - timedelta(days=randint(0, 365))).date()
        recipe.save()
        self.assign_random_tags(recipe)
        return recipe

    def assign_random_tags(self, recipe):
        """Assign a random selection of tags to a recipe."""
        all_dietary = list(DietaryTag.objects.all())
        all_cuisine = list(CuisineTag.objects.all())

        if all_dietary:
            num_dietary = randint(0, min(3, len(all_dietary)))
            selected_dietary = sample(all_dietary, num_dietary)
            recipe.dietary_tags.set(selected_dietary)

        if all_cuisine:
            num_cuisine = randint(0, min(2, len(all_cuisine)))
            selected_cuisine = sample(all_cuisine, num_cuisine)
            recipe.cuisine_tags.set(selected_cuisine)

    def create_ingredients(self):
        """Create ingredients for all recipes."""
        recipes = Recipe.objects.all()
        ingredient_names = [
            'flour', 'sugar', 'butter', 'eggs', 'milk', 'salt', 'pepper',
            'onions', 'garlic', 'tomatoes', 'chicken', 'beef', 'pork',
            'fish', 'rice', 'pasta', 'cheese', 'olive oil', 'chocolate',
            'vanilla', 'baking powder', 'yeast', 'carrots', 'potatoes',
            'bell peppers', 'mushrooms', 'spinach', 'lettuce', 'lemon',
            'lime', 'herbs', 'spices', 'soy sauce', 'vinegar', 'broth'
        ]
        units = ['g', 'ml', 'kg', 'L', 'oz']
        total = recipes.count()
        current = 0
        for recipe in recipes:
            current += 1
            print(f"Seeding ingredients {current}/{total}", end='\r')
            if RecipeIngredient.objects.filter(recipe=recipe).count() == 0:
                self.add_ingredients_to_recipe(recipe, ingredient_names, units)
        print("Ingredient seeding complete.")

    def add_ingredients_to_recipe(self, recipe, ingredient_names, units):
        """Add random ingredients to a recipe."""
        num_ingredients = randint(3, 8)
        for _ in range(num_ingredients):
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=choice(ingredient_names),
                amount=randint(1, 500),
                units=choice(units)
            )

    def create_comments(self):
        """Create comments on recipes."""
        recipes = list(Recipe.objects.all())
        users = list(User.objects.all())
        
        fixture_usernames = ['@johndoe', '@janedoe', '@charlie']
        fixture_recipes = Recipe.objects.filter(author__username__in=fixture_usernames)
        
        print("Seeding fixture recipe comments...")
        for recipe in fixture_recipes:
            num_comments = randint(3, 8)
            commenters = sample(users, min(num_comments, len(users)))
            self.add_comments_to_recipe(recipe, commenters)
        
        print("Seeding random comments...")
        total = len(recipes)
        for i, recipe in enumerate(recipes):
            print(f"Seeding comments {i+1}/{total}", end='\r')
            num_comments = randint(2, 10)
            commenters = sample(users, min(num_comments, len(users)))
            self.add_comments_to_recipe(recipe, commenters)
        print("Comment seeding complete.")
    
    def add_comments_to_recipe(self, recipe, commenters):
        """Add comments from commenters to a recipe."""
        for commenter in commenters:
            try:
                comment, created = Comment.objects.get_or_create(
                    recipe=recipe,
                    author=commenter,
                    defaults={'text': self.faker.text(max_nb_chars=100)}
                )
                if created:
                    comment.timestamp = timezone.now() - timedelta(days=randint(0, 30))
                    comment.save()
            except:
                pass

    def create_ratings(self):
        """Create ratings on recipes."""
        recipes = list(Recipe.objects.all())
        users = list(User.objects.all())
        
        print("Seeding ratings...")
        total = len(recipes)
        for i, recipe in enumerate(recipes):
            print(f"Seeding ratings {i+1}/{total}", end='\r')
            num_ratings = randint(5, 20)
            raters = sample(users, min(num_ratings, len(users)))
            self.add_ratings_to_recipe(recipe, raters)
        print("Rating seeding complete.")
    
    def add_ratings_to_recipe(self, recipe, raters):
        """Add ratings from raters to a recipe."""
        for rater in raters:
            try:
                Rating.objects.get_or_create(
                    recipe=recipe,
                    user=rater,
                    defaults={'rating': randint(1, 5)}
                )
            except:
                pass

    def create_follows(self):
        """Create follow relationships between users."""
        users = list(User.objects.all())
        
        fixture_usernames = ['@johndoe', '@janedoe', '@charlie']
        fixture_users = []
        for username in fixture_usernames:
            try:
                fixture_users.append(User.objects.get(username=username))
            except:
                pass
        
        print("Seeding fixture user follows...")
        for user in fixture_users:
            self.add_follows_for_user(user, fixture_users)
        
        print("Seeding random follows...")
        total = len(users)
        for i, user in enumerate(users):
            print(f"Seeding follows {i+1}/{total}", end='\r')
            num_follows = randint(5, 30)
            following = sample(users, min(num_follows, len(users)))
            self.add_follows_for_user(user, following)
        print("Follow seeding complete.")
    
    def add_follows_for_user(self, user, users_to_follow):
        """Add follow relationships for a user."""
        for other in users_to_follow:
            if user != other:
                try:
                    Follow.objects.get_or_create(follower=user, following=other)
                except:
                    pass

    def create_favourites(self):
        """Create favourite recipe relationships."""
        recipes = list(Recipe.objects.all())
        users = list(User.objects.all())
        
        print("Seeding favourites...")
        total = len(users)
        for i, user in enumerate(users):
            print(f"Seeding favourites {i+1}/{total}", end='\r')
            num_favs = randint(3, 15)
            fav_recipes = sample(recipes, min(num_favs, len(recipes)))
            self.add_favourites_for_user(user, fav_recipes)
        print("Favourite seeding complete.")
    
    def add_favourites_for_user(self, user, recipes):
        """Add favourite recipes for a user."""
        for recipe in recipes:
            try:
                Favourite.objects.get_or_create(user=user, recipe=recipe)
            except:
                pass


def create_username(first_name, last_name):
    """
    Construct a simple username from first and last names.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: A username in the form ``@{firstname}{lastname}`` (lowercased).
    """
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    """
    Construct a simple example email address.

    Args:
        first_name (str): Given name.
        last_name (str): Family name.

    Returns:
        str: An email in the form ``{firstname}.{lastname}@example.org``.
    """
    return first_name + '.' + last_name + '@example.org'
