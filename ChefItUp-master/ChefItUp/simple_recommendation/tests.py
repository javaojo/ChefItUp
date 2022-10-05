from django.test import TestCase

from ChefItUp.simple_recommendation.models import PopularRecipe
from ChefItUp.simple_recommendation.recommendations import get_all_top_recipes, get_random_top_recipes
from ChefItUp.simple_recommendation.updater import update_popular_table, get_favourite_amount

if __name__ == '__main__':
    import django
    django.setup()
    TestCase.main()


class TestSimpleRecommendation(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up 6 saved recipes with different save counts
        :return:
        """
        super(TestSimpleRecommendation, cls).setUpClass()

        # Save 1st recipe 5 times
        update_popular_table(633508, True)
        update_popular_table(633508, True)
        update_popular_table(633508, True)
        update_popular_table(633508, True)
        update_popular_table(633508, True)

        # Save 2nd recipe 4 times
        update_popular_table(634873, True)
        update_popular_table(634873, True)
        update_popular_table(634873, True)
        update_popular_table(634873, True)

        # Save 3rd recipe 3 times
        update_popular_table(782600, True)
        update_popular_table(782600, True)
        update_popular_table(782600, True)

        # Save 4th recipe 2 times
        update_popular_table(655575, True)
        update_popular_table(655575, True)

        # Save 5th recipe 1 time
        update_popular_table(648320, True)

        # Save 6th recipe 1 time
        update_popular_table(661640, True)

    def test_get_all_top_recipes(self):
        """
        Checks that the list of all saved recipes is retrieved correctly
        :return:
        """
        print("Get all top recipes")
        print(get_all_top_recipes())
        # Assert that every recipe id is correct
        self.assertListEqual([633508, 634873, 782600, 655575, 648320, 661640], get_all_top_recipes())

    def test_updater_save(self):
        """
        Checks that each saved recipes has the correct saved count
        :return:
        """
        # Assert the favourite count of each recipe
        print("Test updater for saving recipes")
        self.assertEqual(5, get_favourite_amount(633508))
        self.assertEqual(4, get_favourite_amount(634873))
        self.assertEqual(3, get_favourite_amount(782600))
        self.assertEqual(2, get_favourite_amount(655575))
        self.assertEqual(1, get_favourite_amount(648320))
        self.assertEqual(1, get_favourite_amount(661640))

    def test_updater_unsave(self):
        """
        Checks that recipe gets removed when unsaved
        :return:
        """
        # Remove recipe/decrease save count of recipe from popular recipe table
        update_popular_table(661640, False)
        update_popular_table(633508, False)

        print("Test updater for unsaving recipes")
        # Asserts the favourite count of the recipe that was unsaved
        self.assertEqual(None, get_favourite_amount(661640))
        self.assertEqual(4, get_favourite_amount(633508))

        # Asserts that the list of recipe ids should not contain recipe id 661640
        print("Get new all top recipes")
        print(get_all_top_recipes())
        self.assertListEqual([633508, 634873, 782600, 655575, 648320], get_all_top_recipes())

    def test_get_random_top_recipes(self):
        """
        Checks that the returned random recipes are correct
        :return:
        """
        # TODO check if assert makes sense

        print("Get random top recipes")
        random_list = get_random_top_recipes(3)
        # Assert that each recipe is within the list of saved recipes
        self.assertIn(random_list[0], [633508, 634873, 782600, 655575, 648320, 661640])
        self.assertIn(random_list[1], [633508, 634873, 782600, 655575, 648320, 661640])
        self.assertIn(random_list[2], [633508, 634873, 782600, 655575, 648320, 661640])

    def test_no_recipes_saved(self):
        """
        Test that list should be empty if no recipes have been saved
        :return: None
        """
        # Delete all recipes from table
        PopularRecipe.objects.all().delete()

        # Assert that the list of recipe ids should be empty
        print("Test getting top recipes with no recipes saved")
        self.assertListEqual([], get_all_top_recipes())

    @classmethod
    def tearDownClass(cls):
        super(TestSimpleRecommendation, cls).tearDownClass()
        # Delete all recipes from table if they exist
        if PopularRecipe.objects.exists():
            PopularRecipe.objects.all().delete()
