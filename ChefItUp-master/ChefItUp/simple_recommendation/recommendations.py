from ChefItUp.simple_recommendation.updater import *
import django
import random

N_OF_TOP_RECIPES = 25


def get_all_top_recipes():
    """
    Returns list of spoonacular ids of all popular recipes.
    Relies on ordering by fav_count on PopularRecipe model
    :return: list of ids of first N_OF_TOP_RECIPES popular recipes, [] if empty
    """
    top_n_query_set = PopularRecipe.objects.all()[:N_OF_TOP_RECIPES]
    return list(map(lambda recipe: recipe.recipe_id, list(top_n_query_set)))


def get_random_top_recipes(n: int):
    """
    Get random recipe ids popular recipes
    :param n: number of recipes to return
    :return: list of n random recipe ids
    """
    top_recipes = get_all_top_recipes()
    if len(top_recipes) > 0: #and n < len(top_recipes):
        return random.sample(get_all_top_recipes(), n)
    else:
        print(f"simple recommender is about to return nothing. top_recipes: {top_recipes}")
        return []
