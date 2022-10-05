import os

import django
from django.db.models import F

from ChefItUp.simple_recommendation.models import PopularRecipe
from datetime import datetime

# TOP_RECIPES_FILE_NAME = 'top_recipes.json'
MIN_FAV_RECIPES_COUNT = 25


def update_popular_table(recipe_id: int, favourite: bool) -> None:
    """
    :param recipe_id: id of the recipe added or removed from saved
    :param favourite: True if user adds the recipe to saved and False if they remove it
    :return:
    :except RuntimeError: if favourite is False, but there is no such recipe in the table -
    possibly update function wasn't called
    """
    recipe = PopularRecipe.objects.filter(recipe_id=recipe_id).first()
    if recipe:  # there is already a recipe
        if favourite:  # and user wants to save it
            recipe.fav_count = F('fav_count') + 1
            recipe.save()
        else:  # user deletes it from their saved
            if recipe.fav_count == 1:  # if user was the only one who had it in saved
                recipe.delete()
                return
            else:  # if more users have it saved
                recipe.fav_count = F('fav_count') - 1
                recipe.save()
    else:  # if there is no this recipe in the table yet
        if favourite:
            recipe = PopularRecipe(recipe_id=recipe_id, fav_count=1)
            recipe.save()
        else:
            RuntimeError("There is no recipe in the table to remove")


# def update_top_file():
#
#     # TODO what if there is not enough elements in the db or no elements at all
#     #df_top = get_top_dataframe().nlargest(N_OF_TOP_RECIPES, 'fav_count')
#     if (PopularRecipe.objects.exists()) & (PopularRecipe.objects.count() >= MIN_FAV_RECIPES_COUNT):
#         top_list = list(PopularRecipe.objects.values_list('recipe_id', flat=True).order_by('-fav_count')[:25])
#         #print(top_list)
#         return top_list
#     else:
#         print("Too few popular recipes to recommend")
#         return False


#    # Delete file if exists
#    # if os.path.exists(TOP_RECIPES_FILE_NAME):
#    #     os.remove(TOP_RECIPES_FILE_NAME)

#     df_top[['recipe_id']].to_json(TOP_RECIPES_FILE_NAME, orient='values')

#
#
# def get_recipe_id(recipe_id: int):
#     recipe = PopularRecipe.objects.filter(recipe_id=recipe_id).first()
#     if recipe:
#         return recipe.recipe_id
#     else:
#         return "; recipe does not exist"
#
#


def get_favourite_amount(recipe_id: int):
    recipe = PopularRecipe.objects.filter(recipe_id=recipe_id).first()
    if recipe:
        return recipe.fav_count
    else:
        return None


# update_top_file()
