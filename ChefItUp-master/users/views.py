from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from users.models import SavedRecipe

from django.conf import settings

from django.shortcuts import redirect

from django.shortcuts import render
from .forms import DietPreferenceForm, UpdateProfile
from .models import DietPreference


def profile(request):
    global saved_recipes
    global password_change_form

    if request.user.is_authenticated:
        saved_recipes_set = SavedRecipe.objects.filter(custom_user_id=request.user.id)
        saved_recipes_ids = []
        saved_recipes = []

        for saved_recipe in saved_recipes_set:
            saved_recipes_ids.append(saved_recipe.recipe_id)

        saved_recipes_ids = ",".join(map(lambda recipe_id: str(recipe_id), saved_recipes_ids))

        saved_recipes = settings.SPOONACULAR_API.get_recipe_information_bulk(ids=saved_recipes_ids).json()

        RECIPELIST = []

        if not 'status' in saved_recipes:
            RECIPELIST = list(map(lambda recipe_dict: {
                'title': recipe_dict.get('title'),
                'vegan': recipe_dict.get('vegan'),
                'img': recipe_dict.get('image'),
                'id': recipe_dict.get('id'),
                'img': recipe_dict.get('image')
            }, saved_recipes))
    else:
        return redirect('/')

    # Password change form
    password_change_form = PasswordChangeForm(request.user)

    # Edit profile form
    update_profile_form = UpdateProfile(instance=request.user)

    return render(request, "registration/_profile.html", {"form": {},
                                                          "saved_recipes": RECIPELIST,
                                                          'password_change_form': password_change_form,
                                                          'update_profile_form': update_profile_form
                                                          })


def convert_to_dict(list):
    RECIPELIST = list(map(lambda recipe_dict: {
        'title': recipe_dict.get('title'),
        'vegan': recipe_dict.get('vegan'),
        'img': recipe_dict.get('image'),
        'id': recipe_dict.get('id'),
        'img': recipe_dict.get('image')
    }, list))

    return RECIPELIST


# returns preference of user as a dictionary
def get_preferences(user_id):
    if DietPreference.objects.filter(pk=user_id).exists():
        preferences = DietPreference.objects.get(pk=user_id)
        print(preferences)
        # load their choices
        data = {'ketogenic': preferences.ketogenic, 'dairy_free': preferences.dairy_free,
                'vegetarian': preferences.vegetarian, 'vegan': preferences.vegan,
                'gluten_free': preferences.gluten_free}
        return data
    else:
        return None


def update_profile(request):
    if request.method == "POST":
        form = UpdateProfile(request.POST, instance=request.user)
        form.actual_user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated successfully")

            return redirect('/profile/')
        else:
            messages.warning(request, "Please make sure your information is in the right format")
            return redirect('/profile/')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/profile')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('/profile')
