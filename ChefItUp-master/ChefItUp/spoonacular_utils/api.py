# Spoonacular API
# Spoonacular API
# Copyright
# 2018 John W. Miller (original author)
# 2020 Dmitry Fedorenko (modified)
# https://github.com/johnwmillr/SpoonacularAPI/blob/master/spoonacular/api.py

"""
API details and documentation: https://spoonacular.com/food-api
To use instantiate once API class with spoonacular API key as an argument in views.py or similar file.
"""

import requests
import socket
import time


def formatMethodName(name):
    name = name.lower().replace('(', '').replace(')', '')
    return name.replace(' ', '_')


class API(object):
    """Spoonacular API"""

    # Create a persistent requests connection
    session = requests.Session()
    session.headers = {"Application": "spoonacular",
                       "Content-Type": "application/x-www-form-urlencoded"}

    def __init__(self, api_key, timeout=5, sleep_time=1.5, allow_extra_calls=False):
        """ Spoonacular API Constructor
        :param api_key: key provided by Spoonacular (str)
        :param timeout: time before quitting on response (seconds)
        :param sleep_time: time to wait between requests (seconds)
        :param allow_extra_calls: override the API call limit (bool)
        """

        assert api_key != '', 'Must supply a non-empty API key.'
        self.api_key = api_key
        self.api_root = "https://api.spoonacular.com/"
        self.timeout = timeout
        self.sleep_time = max(sleep_time, 1)  # Rate limiting
        self.allow_extra_calls = allow_extra_calls

    @classmethod
    def convert_to_dict(cls, reduced_list):
        recipe_list = list(map(lambda recipe_dict: {
            'title': recipe_dict.get('title'),
            'vegan': recipe_dict.get('vegan'),
            'id': recipe_dict.get('id'),
            'img': 'https://spoonacular.com/recipeImages/{}-556x370.jpg'.format(recipe_dict.get('id')),
        }, reduced_list))

        return recipe_list
    def _make_request(self, path, method='GET',
                      query_=None, params_=None, json_=None):
        """ Make a request to the API
        returns None in case of timeout
        returns response with status code 402 if API quota is exceeded.
        """

        try:
            uri = self.api_root + path

            # API auth (temporary kludge)
            if params_:
                params_['apiKey'] = self.api_key
            else:
                params_ = {'apiKey': self.api_key}
            response = self.session.request(method, uri,
                                            timeout=self.timeout,
                                            data=query_,
                                            params=params_,
                                            json=json_)
        except socket.timeout as e:
            print("Timeout raised and caught: {}".format(e))
            return None
        time.sleep(self.sleep_time)  # Enforce rate limiting
        return response

    def get_random_recipes(self, limitLicense=True, number=None, tags=None):
        """ Find random (popular) recipes.
            https://spoonacular.com/food-api/docs#get-random-recipes
        """
        endpoint = "recipes/random"
        url_query = {}
        url_params = {"limitLicense": limitLicense, "number": number, "tags": tags}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def search_recipes_by_name(self, query, fillIngredients=False, limitLicense=True, number=10, diet=None):
        """ Find recipes by name
        :param query: recipe name keyword
        :param fillIngredients: add information about the used and missing ingredients in each recipe.
        :param limitLicense: whether the recipes should have an open license that allows display with proper attribution.
        :param number: number of recipes to return
        :param diet: dietary requirements
        :return: recipe ID, recipe title, time taken, servings, source URL, open license, image
        """
        endpoint = 'recipes/search'
        url_query = {}
        url_params = {"fillIngredients": fillIngredients, "query": query, "limitLicense": limitLicense,
                      "number": number, "diet": diet, "instructionsRequired": True}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def search_recipes_by_ingredients(self, ingredients, fillIngredients=False, limitLicense=True, number=10, diet=None):
        """ Find recipes that use as many of the given ingredients
            as possible and have as little as possible missing
            ingredients. This is a whats in your fridge API endpoint.
            https://spoonacular.com/food-api/docs#search-recipes-by-ingredients
        """
        endpoint = "recipes/findByIngredients"
        url_query = {}
        url_params = {"fillIngredients": fillIngredients, "ingredients": ingredients, "limitLicense": limitLicense,
                      "number": number, "diet": diet, "instructionsRequired": True}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def search_recipes_complex(self, **kwargs):
        """ Search through hundreds of thousands of recipes using advanced
            filtering and ranking. NOTE: This method combines searching by
            query, by ingredients, and by nutrients into one endpoint.
            https://spoonacular.com/food-api/docs#Search-Recipes-Complex
        """
        endpoint = "recipes/complexSearch"
        url_query = {}
        url_params = {**kwargs}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def get_recipe_information(self, id, includeNutrition=None):
        """ Get information about a recipe.
            https://spoonacular.com/food-api/docs#get-recipe-information
        """
        endpoint = "recipes/{id}/information".format(id=id)
        url_query = {}
        url_params = {"includeNutrition": includeNutrition}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def get_recipe_information_bulk(self, ids, includeNutrition=None):
        """ Get information about multiple recipes at once. That
            is equivalent of calling the Get Recipe Information
            endpoint multiple times but is faster. Note that
            each returned recipe counts as one request.
            https://spoonacular.com/food-api/docs#get-recipe-information-bulk
        """
        endpoint = "recipes/informationBulk"
        url_query = {}
        url_params = {"ids": ids, "includeNutrition": includeNutrition}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def autocomplete_recipe_search(self, query, number=None, diet=None):
        """ Autocomplete a partial input to possible recipe names.
            https://spoonacular.com/food-api/docs#autocomplete-recipe-search
        """
        endpoint = "recipes/autocomplete"
        url_query = {}
        url_params = {"number": number, "query": query, "diet": diet, "instructionsRequired": True}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

    def get_similar_recipes(self, id, number=10, diet=None):
        """ Find recipes which are similar to the given one.
            https://spoonacular.com/food-api/docs#get-similar-recipes
            :param number: sets number of recipes to be returned, costs 0.01 points per recipe
            :param diet: sets diet definition
        """
        endpoint = "recipes/{id}/similar".format(id=id)
        url_query = {}
        url_params = {"number": number, "diet": diet, "instructionsRequired": True}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)

