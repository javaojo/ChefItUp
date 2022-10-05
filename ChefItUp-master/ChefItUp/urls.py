"""ChefItUp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from webapp.views import (
    home_view,
    recipe_query,
    contact,
    recipe_view,
    contact,
    update_ingredient_filter,
    search_recipe_by_ingredients,
    save_recipe,
    unsave_recipe,
    login_user,
    register_user,
    ingredient_search,
    update_diet_preferences,
    update_twitter_feed,
    send_tweet,
    remove_ingredient_filter
)

from users.views import (
    profile,
    change_password,
    update_profile
)

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('', include("webapp.urls")),
    path('', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('contact/', contact),
    path('profile/', profile),
    path('change_password/', change_password),
    path('update_profile/', update_profile),
    path('recipe/<int:recipeId>', recipe_view, name="recipe_view"),
    path('save_recipe/', save_recipe, name= "save_recipe"),
    path('unsave_recipe/', unsave_recipe, name= "unsave_recipe"),
    path('ajax_calls/recipe_query', recipe_query, name= "recipe_query"),
    path('ajax_calls/update_ingredient_filter', update_ingredient_filter, name= "update_ingredient_filter"),
    path('ajax_calls/search_recipe_by_ingredients', search_recipe_by_ingredients, name= "search_recipe_by_ingredients"),
    path('ajax_calls/update_diet_preferences', update_diet_preferences, name="update_diet_preferences"),
    path('ajax_calls/update_twitter_feed', update_twitter_feed),
    path('ajax_calls/ingredient_search', ingredient_search),
    path('ajax_calls/remove_ingredient_filter', remove_ingredient_filter),
    path('login_user/', login_user),
    path('register_user/', register_user),
    path('recipe/sendtweet/', send_tweet, name='send_tweet'),
]
