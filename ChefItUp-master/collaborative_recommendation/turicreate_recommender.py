# from django_pandas.io import read_frame
# import turicreate
#
# # import django
# #
# # django.setup()
#
# from users.models import SavedRecipe
#
# # In views the instance of this class will be created.
# # When user save, unsave recipe model will be updated.
# # get_recommendations(user_id, n) can be called called if user logged in
# # TODO: 3 Integrate it with front-end
#
# # Disadvantages, which we are not going to fix:
# # 1. Model creation will be costly for many users. Will significantly slow down server start.
# # 2. Not scalable - recalculating model every save/unsave will have to be replaced with every day/week recalculation
# # 3. SFrames can be saved and loaded to and from the files. Will be useful in production, but no time to implement now
#
# # Recommendations, which predicted score for a certain user will be less or equal to this threshold will be excluded
# SCORE_THRESHOLD = 0.0
#
#
# def _get_train_data():
#     """
#     Convert SavedRecipe Model into an SFrame to be used in turicreate recommender
#     :return: SFrame of SavedRecipe with columns 'user_id' and 'recipe_id'
#     """
#
#     # Get QuerySet of saved recipes
#     qs = SavedRecipe.objects.select_related('custom_user').all()
#     # Convert it to DataFrame
#     saved_recipes_df = read_frame(qs, fieldnames=['custom_user__id', 'recipe_id'])
#     # Rename columns
#     saved_recipes_df.columns = ['user_id', 'recipe_id']
#     # Convert DataFrame to SFrame for Turicreate
#     train_data_sf = turicreate.SFrame(saved_recipes_df)
#
#     return train_data_sf
#
#
# def _get_recommender(train_data):
#     """
#     Creates model for recommender with the passed train data
#     :param train_data: SavedRecipes SFrame
#     :return: recommender model
#     """
#
#     item_sim_recommender = turicreate.item_similarity_recommender.create(train_data, user_id='user_id',
#                                                                          item_id='recipe_id',
#                                                                          similarity_type='cosine')
#     return item_sim_recommender
#
#
# class CollaborativeRecommender:
#     """
#     Singleton which holds the model for collaborative recommendations.
#     Only one instance should exist during the runtime to avoid recalculating the similarities after each object creation
#     Should not be instantiated directly. Use CollaborativeRecommender.get_instance()
#     """
#     __instance = None
#
#     @staticmethod
#     def get_instance():
#         if CollaborativeRecommender.__instance is None:
#             CollaborativeRecommender()
#         return CollaborativeRecommender.__instance
#
#     def __init__(self):
#         if CollaborativeRecommender.__instance is not None:
#             raise Exception("Only one instance of CollaborativeRecommender shoul exist at the same time."
#                             " Use CollaborativeRecommender.get_instance() instead of CollaborativeRecommender()")
#         else:
#             self.update_recommender_model()
#             CollaborativeRecommender.__instance = self
#
#     def get_turicreate_all_recommendations(self):
#         """
#         Get all recommended recipes for all users
#         :return: SFrame with recommended recipe ids, unfiltered.
#         """
#         item_sim_recommendations_sf = self.recommender.recommend()
#
#         return item_sim_recommendations_sf
#
#     def _get_recommendations_sf(self, user_id, n_to_get):
#         """
#          Returns An SFrame with the top ranked items for a certain user.
#                 The columns are: ``user_id``, ``item_id``, *score*, and *rank*,
#                 where ``user_id`` and ``item_id`` match the user and item column names specified at training time.
#                 The rank column is between 1 and ``k`` and gives the relative score of that item.
#                 The value of score depends on the method used for recommendations.
#         :param user_id: id of current user
#         :param n_to_get: number of recipe recommendations to obtain
#         :return: SFrame with recipe ids with a score higher than SCORE_THRESHOLD
#         """
#
#         item_sim_recomm = self.recommender.recommend(users=[user_id], k=n_to_get)
#         filter_recomm_sf = item_sim_recomm[(item_sim_recomm['score'] > SCORE_THRESHOLD)]
#
#         return filter_recomm_sf
#
#     def get_recommendations(self, user_id, n):
#         """
#         Returns the list of recipe_ids to recommend to user
#         :param user_id: user to which to recommend
#         :param n: number of recipes to recommend
#         :return: array of recipe ids to recommend to user. Array may contain less recommendations than requested.
#         """
#         recommendations_sf = self._get_recommendations_sf(user_id, n)
#         return list(recommendations_sf.select_column('recipe_id'))
#
#     def update_recommender_model(self):
#         """
#         Updates train data to input new train data in recommender model.
#         To be called when a user saves a recipe.
#         :return:
#         """
#         train_data = _get_train_data()
#         self.recommender = _get_recommender(train_data=train_data)
