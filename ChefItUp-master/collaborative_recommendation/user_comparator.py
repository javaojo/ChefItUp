from django_pandas.io import read_frame
import numpy as np
from pandas import DataFrame
from sklearn.metrics import pairwise
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors

from users.models import SavedRecipe


# The following code is based on https://cmdlinetips.com/2018/03/how-to-change-column-names-and-row-indexes-in-pandas/
def _get_predicted_rating_matrix(ratings, similarity):
    """

    :param ratings: dataframe of user_id vs recipe_id matrix
    :param similarity: array of arrays of cosine similarity between users
    :return: array of arrays of predicted ratings of recipes (columns) by users (rows)
    """
    mean_user_rating = ratings.mean(axis=1)
    # We use np.newaxis so that mean_user_rating has same format as ratings
    ratings_diff = (ratings - mean_user_rating[:, np.newaxis])  # type DataFrame with user_id and recipe_id
    prediction = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    prediction_df = DataFrame(data=prediction, index=ratings.index, columns=ratings.columns)
    return prediction_df


def _get_saved_recipes_df():
    """
    Returns DataFrame in form of user_id vs recipe_id matrix
    where 1 means that user have saved the recipe and 0 that they did not.
    Example:
    recipe_id   42     451
    user_id
    1           1       0
    2           0       1

    :return: pandas dataframe of saved recipes

    """
    # Get the queryset of all saved recipes
    qs = SavedRecipe.objects.select_related('custom_user').all()

    # Convert it to dataframe, leaving only required fields
    # recipe_id and id of the user from custom_user object, by accessing it via __
    saved_recipes_df = read_frame(qs, fieldnames=['custom_user__id', 'recipe_id'])

    # Rename columns
    saved_recipes_df.columns = ['user_id', 'recipe_id']

    # Add rating column for pivot to work with. 1 - recipe saved, 0 - not saved
    saved_recipes_df['rating'] = 1

    # Reshape dataframe from

    # | user_id | recipe_id |
    # |    1    |    42     |
    # |    2    |    451    |

    # to

    # recipe_id   42     451
    # user_id
    # 1           1       0
    # 2           0       1

    saved_recipes_df = saved_recipes_df.pivot_table(index='user_id', columns='recipe_id', values='rating', fill_value=0)
    return saved_recipes_df


def _get_user_similarity():
    """
    Returns user similarity matrix in form of array of arrays of cosine distances.
    Note that values closer to 0 means more similar, closer to 1 - less similar
    Example:
    [[2.22044605e-16 1.83503419e-01 1.00000000e+00]
    [1.83503419e-01 0.00000000e+00 1.00000000e+00]
    [1.00000000e+00 1.00000000e+00 0.00000000e+00]]
    :return:
    """
    # Get DataFrame table of user_ids vs recipe_ids
    saved_recipes_df = _get_saved_recipes_df()
    # Feed the table to scipy knn algorithm to get (user_id, user_id) similarities table
    # user_similarity = pairwise_distances(saved_recipes_df, metric='cosine') # 3x3 matrix
    user_similarity = pairwise.cosine_similarity(saved_recipes_df)
    user_similarity_df = DataFrame(data=user_similarity, index=saved_recipes_df.index, columns=saved_recipes_df.index)
    return user_similarity_df


# def _get_user_similarity_knn():
#      #Get DataFrame table of user_ids vs recipe_ids
#     saved_recipes_df = _get_saved_recipes_df()
#     #n_neighbours value cant be hard coded
#     knn_model = NearestNeighbors(algorithm='brute', metric='cosine', n_neighbors=2)
#     knn_model.fit(saved_recipes_df)
#     distances = knn_model.kneighbors()
#     print(distances)
    #raw_recommends = sorted(
        #list(
        #    zip(
       #         distances.squeeze().tolist()
      #      )
     #   )
    #)
    #for i, (dist) in enumerate(raw_recommends):
    #    print({1})
