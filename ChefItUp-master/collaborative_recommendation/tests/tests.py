# these two lines prevent error "django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet."
# need to be called before importing any models
import django
django.setup()

from django.test import TestCase

from collaborative_recommendation.user_comparator import _get_saved_recipes_df, \
    _get_user_similarity, _get_predicted_rating_matrix
from users.models import CustomUser, SavedRecipe


# Problems launching tests:
# django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured.
#   add DJANGO_SETTINGS_MODULE=ChefItUp.settings to the run configuration environment variables.

class TestCollaborativeRecommender(TestCase):
    user1 = None
    user2 = None
    user3 = None

    @classmethod
    def setUpClass(cls):
        """
        Create 3 users to test
        Set up saved recipes for the 3 users
        :return:
        """
        # get recommendation for user 1
        super(TestCollaborativeRecommender, cls).setUpClass()

        # User to give recommendations to
        cls.user1 = CustomUser.objects.create(id=1, username='username1')
        # User with similar tastes to user1 and extra saved recipes
        cls.user2 = CustomUser.objects.create(id=2, username='username2')
        # User with different taste to user1
        cls.user3 = CustomUser.objects.create(id=3, username='username3')

        SavedRecipe.objects.create(custom_user=cls.user1, recipe_id=633508)
        SavedRecipe.objects.create(custom_user=cls.user1, recipe_id=634873)

        SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=633508)
        SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=634873)
        SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=782600)

        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=655575)
        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=648320)
        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=660368)

    def test_dataframe_loads(self):
        df = _get_saved_recipes_df()
        print("user_id vs recipe_id dataframe:")
        print(df)
        print()
        self.assertEqual("user_id", df.index.name)
        self.assertEqual("recipe_id", df.columns.name)
        self.assertEqual(6, len(df.columns))
        self.assertEqual(3, len(df.index))

    def test_user_similarity_matrix(self):
        user_similarity_matrix = _get_user_similarity()
        print("user_id vs user_id cosine similarity:")
        print(user_similarity_matrix)
        print()

    def test_predictions(self):
        saved_recipes = _get_saved_recipes_df()
        user_similarity_matrix = _get_user_similarity()

        user_prediction = _get_predicted_rating_matrix(saved_recipes, user_similarity_matrix)
        print("Prediction. User_id vs recipe_id: ")
        print(user_prediction)
        print()


    @classmethod
    def tearDownClass(cls):
        super(TestCollaborativeRecommender, cls).tearDownClass()
        cls.user1.delete()
        cls.user2.delete()
        cls.user3.delete()

