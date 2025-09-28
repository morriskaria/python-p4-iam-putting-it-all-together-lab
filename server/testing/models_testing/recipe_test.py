import pytest
from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Test cases for the Recipe model in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user first
            user = User(
                username="testuser",
                image_url="http://example.com/image.jpg",
                bio="Test bio"
            )
            user.password_hash = "password"
            db.session.add(user)
            db.session.commit()

            # Now create recipe with the user
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            # Verify the recipe was created with attributes
            created_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()
            assert created_recipe.title == "Delicious Shed Ham"
            assert created_recipe.instructions is not None
            assert created_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():

            user = User(
                username="testuser2",
                image_url="http://example.com/image2.jpg",
                bio="Test bio 2"
            )
            user.password_hash = "password"
            db.session.add(user)
            db.session.commit()

            with pytest.raises(ValueError):
                # Create recipe and explicitly set attributes to trigger validation
                recipe = Recipe()
                recipe.instructions = "Valid instructions that are long enough to pass validation for the recipe model"
                recipe.minutes_to_complete = 60
                recipe.user_id = user.id
                # Setting title to None should trigger the validation
                recipe.title = None

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters long.'''

        with app.app_context():

            user = User(
                username="testuser3",
                image_url="http://example.com/image3.jpg",
                bio="Test bio 3"
            )
            user.password_hash = "password"
            db.session.add(user)
            db.session.commit()

            with pytest.raises(ValueError):
                # Create recipe and explicitly set attributes to trigger validation
                recipe = Recipe()
                recipe.title = "Valid Title"
                recipe.minutes_to_complete = 60
                recipe.user_id = user.id
                # Setting short instructions should trigger the validation
                recipe.instructions = "Too short"
                