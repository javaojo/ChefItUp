import unittest

# The actual module name is django-environ
from ChefItUp import settings
from ChefItUp.spoonacular_utils.api import API

SPOONACULAR_API_KEY = settings.SPOONACULAR_API_KEY

N_OF_RECIPES_TO_GET = 2


class TestSpoonacularApi(unittest.TestCase):
    def setUp(self):
        self.api = API(SPOONACULAR_API_KEY)

    def test_search_by_ingredients(self):
        print("test_search_by_ingredients\n")
        ingredients = ["cheese", "milk"]
        ingredients_string = ",".join(ingredients)
        print(ingredients_string)
        response = self.api.search_recipes_by_ingredients(ingredients_string, number=N_OF_RECIPES_TO_GET)

        print(response)
        print(f"response.status_code: {response.status_code}")
        print(f"response.headers: {response.headers}")
        print(f"response.text: {response.text}")
        print(f"response.json: {response.json}")


    def test_search_by_query(self):
        print("test_search_by_query\n")
        query = "shepherd"
        response = self.api.search_recipes_by_name(query, number=N_OF_RECIPES_TO_GET)

        print(response)
        print(f"response.status_code: {response.status_code}")
        print(f"response.headers: {response.headers}")
        print(f"response.text: {response.text}")
        print(f"response.json: {response.json}")


if __name__ == '__main__':
    unittest.main()

