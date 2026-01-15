from django.core.management.base import BaseCommand, CommandError
from recipes.models import User, Recipe, Comment, Rating, Follow, Favourite, DietaryTag, CuisineTag, RecipeIngredient

class Command(BaseCommand):
    """
    Management command to remove (unseed) user data from the database.

    This command deletes all non-staff users from the database. It is designed
    to complement the corresponding "seed" command, allowing developers to
    reset the database to a clean state without removing administrative users.

    Attributes:
        help (str): Short description displayed when running
            `python manage.py help unseed`.
    """
    
    help = 'Removes seeded data from the database'

    def handle(self, *args, **options):
        """
        Execute the unseeding process.

        Deletes all seeded data including users, recipes, comments, ratings,
        follows, favourites, and tags. Preserves administrative accounts.

        Args:
            *args: Positional arguments passed by Django (not used here).
            **options: Keyword arguments passed by Django (not used here).

        Returns:
            None
        """

        print("Unseeding favourites...")
        Favourite.objects.all().delete()
        
        print("Unseeding follows...")
        Follow.objects.all().delete()
        
        print("Unseeding ratings...")
        Rating.objects.all().delete()
        
        print("Unseeding comments...")
        Comment.objects.all().delete()
        
        print("Unseeding ingredients...")
        RecipeIngredient.objects.all().delete()
        
        print("Unseeding recipes...")
        Recipe.objects.all().delete()
        
        print("Unseeding tags...")
        DietaryTag.objects.all().delete()
        CuisineTag.objects.all().delete()
        
        print("Unseeding users...")
        User.objects.filter(is_staff=False).delete()
        
        print("Unseeding complete.")
