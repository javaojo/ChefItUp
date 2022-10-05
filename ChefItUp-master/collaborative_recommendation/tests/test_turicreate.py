# these two lines prevent error "django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet."
# need to be called before importing any models
import django

django.setup()

import numpy as np
from django.test import TestCase
from users.models import CustomUser, SavedRecipe
from collaborative_recommendation.turicreate_recommender import CollaborativeRecommender, _get_train_data


# Problems launching tests:
# django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured.
# Solution: Add DJANGO_SETTINGS_MODULE=ChefItUp.settings to the run configuration environment variables.


class TestTuricreateRecommender(TestCase):
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
        super(TestTuricreateRecommender, cls).setUpClass()

        # User to give recommendations to
        cls.user1 = CustomUser.objects.create(id=1, username='username1')
        # User with similar tastes to user1 and extra saved recipes
        cls.user2 = CustomUser.objects.create(id=2, username='username2')
        # User with different taste to user1
        cls.user3 = CustomUser.objects.create(id=3, username='username3')

        # Add some saved recipes
        SavedRecipe.objects.create(custom_user=cls.user1, recipe_id=633508)
        SavedRecipe.objects.create(custom_user=cls.user1, recipe_id=634873)

        SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=633508)
        SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=634873)
        cls.recipe_to_recommend = SavedRecipe.objects.create(custom_user=cls.user2, recipe_id=782600)

        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=655575)
        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=648320)
        SavedRecipe.objects.create(custom_user=cls.user3, recipe_id=660368)

        cls.recommender = CollaborativeRecommender()

    def test_sframe_loads(self):
        """
        Test that SavedRecipes models are loading into SFrame
        :return: None
        """
        print("test_sframe_loads: user_id recipe_id SFrame:")
        train_data_sf = _get_train_data()
        print(train_data_sf)

        # Get column names
        col_user_id = train_data_sf.column_names()[0]
        col_recipe_id = train_data_sf.column_names()[1]

        # Assert column names
        self.assertEqual("user_id", col_user_id)
        self.assertEqual("recipe_id", col_recipe_id)

        # Assert number of columns and rows
        self.assertEqual(2, train_data_sf.num_columns())
        self.assertEqual(8, train_data_sf.num_rows())

    def test_all_predictions(self):
        # TODO: change to the current needs
        """
        Test sframe of all recommendation results
        :return:
        """
        # Get all recommendations
        recommendations_sf = self.recommender.get_turicreate_all_recommendations()
        print("Get all recommendations")
        print(recommendations_sf)

        # Assert number of columns and rows
        self.assertEqual(4, recommendations_sf.num_columns())
        self.assertEqual(10, recommendations_sf.num_rows())

        # Assert values of user id, recipe ids, score and rank
        np.testing.assert_array_equal([1, 1, 1, 1, 2, 2, 2, 3, 3, 3], recommendations_sf.select_column('user_id'))
        np.testing.assert_array_equal([782600, 655575, 648320, 660368, 655575, 648320, 660368, 633508, 634873, 782600],
                                      recommendations_sf.select_column('recipe_id'))
        np.testing.assert_allclose([0.7071067690849304, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                   recommendations_sf.select_column('score'))
        np.testing.assert_array_equal([1, 2, 3, 4, 1, 2, 3, 1, 2, 3], recommendations_sf.select_column('rank'))

    def test_get_exact_recommendations(self):
        """
        Test that recommender suggests expected recipes.
        :return:
        """
        # Get 1 filtered recommendation for user1
        recommendations_arr = self.recommender.get_recommendations(user_id=1, n=1)
        print("Get exact filtered recommendation")
        print(recommendations_arr)

        # Check that only one recipe is returned
        self.assertEqual(1, len(recommendations_arr))

        # Check that this is the expected recipe
        self.assertEqual(self.recipe_to_recommend.recipe_id, recommendations_arr[0])

    def test_get_available_recommendations(self):
        """
        Test that recommender only returns available recipes even if
        the requested number is larger than available recipes to be recommended
        :return:
        """
        # Attempt to get 3 recoommendations for user1
        recommendations_arr = self.recommender.get_recommendations(user_id=1, n=3)
        print("Get available filtered recommendation")
        print(recommendations_arr)

        # Check that only one recipe is returned
        self.assertEqual(1, len(recommendations_arr))

        # Check that this is the expected recipe
        self.assertEqual(self.recipe_to_recommend.recipe_id, recommendations_arr[0])

    def test_new_updated_recommendations(self):
        """
        Test that train data gets updated when user saves a new recipe
        :return:
        """
        # Add a new saved recipe to user3
        SavedRecipe.objects.create(custom_user=self.user3, recipe_id=631750)

        # Update the train data for recommender
        self.recommender.update_recommender_model()

        # Get all recommendations
        recommendations_sf = self.recommender.get_turicreate_all_recommendations()
        print("Get all updated recommendations")
        print(recommendations_sf)

        # Assert number of columns and rows
        self.assertEqual(4, recommendations_sf.num_columns())
        self.assertEqual(11, recommendations_sf.num_rows())

    def test_no_recipes_saved(self):
        """
        Test that recommender does not return any results if no recipes have been saved
        :return: None
        """
        # Delete all users
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()

        # Update the train data for recommender
        self.recommender.update_recommender_model()

        # Attempt to get recommendations
        recommendations_arr = self.recommender.get_recommendations(user_id=1, n=1)
        print("No recipes saved")

        # Assert that the result should be None
        self.assertEqual(None, recommendations_arr)

    @classmethod
    def tearDownClass(cls):
        super(TestTuricreateRecommender, cls).tearDownClass()

        # Delete users if they exist in SavedRecipes model
        if cls.user1.id is not None:
            cls.user1.delete()
        if cls.user2.id is not None:
            cls.user2.delete()
        if cls.user3.id is not None:
            cls.user3.delete()

        cls.recommender = None
