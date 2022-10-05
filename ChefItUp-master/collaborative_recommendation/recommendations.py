def _get_similar_users(user_id):
    pass
    # SimilarUser.objects.filter(user_id=user_id)
    # if no similar users found:
    #   return None


def _get_distinct_saved_recipes(to_user_id, from_user_id):
    pass
    # get the lists of recipes which are not presented in the first user, but presented in the second
    #


def get_collaborative_recommendations(user_id: int, n: int):
    pass
    # all_recipes_to_suggest
    # similar_users = _get_similar_users(user_id)
    # if similar_users not None:
    #   return None
    # else:
    #   for similar_user_id in similar_users:
    #       all_recipes_to_suggest.extend(_get_distinct_saved_recipes(user_id, similar_user_id))
    # if n > all_recipes_to_suggest.size:
    #   return all_recipes_to_suggest
    # else:
    #   return random n recipes from all_recipes_to_suggest
