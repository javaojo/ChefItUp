from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import HttpResponse
import tweepy
from ast import literal_eval

from users.forms import DietPreferenceForm, RegisterForm
from users.views import get_preferences
from ChefItUp.simple_recommendation import models, updater, recommendations
# from collaborative_recommendation import turicreate_recommender
from users.models import DietPreference, SavedRecipe
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver

# recipes saved by user
global saved_recipes


@receiver(user_signed_up)
def setup_diet_preferences(sender, **kwargs):
    # Creating Diet Preferences if it doesn't exists
    user_id = kwargs['request'].user.id

    if not DietPreference.objects.filter(pk=user_id).first():
        DietPreference.objects.create(custom_user_id=user_id, dairy_free=0, vegetarian=0, vegan=0, gluten_free=0,
                                      ketogenic=0)

@receiver(user_logged_in)
def setup_diet_preferences(sender, **kwargs):
    # Creating Diet Preferences if it doesn't exists
    user_id = kwargs['request'].user.id

    if not DietPreference.objects.filter(pk=user_id).first():
        DietPreference.objects.create(custom_user_id=user_id, dairy_free=0, vegetarian=0, vegan=0, gluten_free=0,
                                      ketogenic=0)

def contact(request):
    if request.method == 'POST':

        # Mail to ChefItUp
        try:
            send_mail(
                request.POST['name'],  # Subject
                "Message from {name}, {email}\n\n\"{message}\"".format(
                    name=request.POST['name'], email=request.POST['email'],
                    message=request.POST['message']
                ),  # Message body
                'contact@chefitup.live',  # From email
                ['chefitup@gmail.com'],  # To email (Needs to be changed)
                fail_silently=False,
            )

            # Mail to user

            send_mail(
                request.POST['name'],  # Subject
                "Hi {name}, we've got your message and will be in touch shortly. \n\n\"{message}\"".format(
                    name=request.POST['name'], email=request.POST['email'],
                    message=request.POST['message']
                ),  # Message body
                'contact@chefitup.live',  # From email
                [request.POST['email']],  # To email (Needs to be changed)
                fail_silently=False,
            )

            messages.success(request, "Your message was sent successfully")
            return redirect('/', {})
        except Exception as e:
            print(e)
            messages.error(request, "Could not send your message")
            return redirect('/#contact')


def reset_diet_preferences(preferences):
    preferences.ketogenic = False
    preferences.vegan = False
    preferences.vegetarian = False
    preferences.dairy_free = False
    preferences.gluten_free = False


def remove_ingredient_filter(request):
    clickedIngredient = request.GET.get('clicked_ingredient')

    if 'clicked_ingredients' not in request.session:
        request.session['clicked_ingredients'] = []

    clicked_ingredients_list = request.session['clicked_ingredients']

    if clickedIngredient in clicked_ingredients_list:
        clicked_ingredients_list.remove(clickedIngredient)

        request.session['clicked_ingredients'] = clicked_ingredients_list

    html = render_to_string('_selected_ingredients.html', {'selectedIngredients': clicked_ingredients_list})
    return HttpResponse(html)
    

def update_diet_preferences(request):
    diet_preference = request.GET.get('diet_preference')

    if DietPreference.objects.filter(custom_user_id=request.user.id).first():
        preferences = DietPreference.objects.get(pk=request.user.id)

        if diet_preference == 'Vegan':
            if not preferences.vegan:
                reset_diet_preferences(preferences)
                preferences.vegan = True
            else:
                reset_diet_preferences(preferences)
        elif diet_preference == 'Vegetarian':
            if not preferences.vegetarian:
                reset_diet_preferences(preferences)
                preferences.vegetarian = True
            else:
                reset_diet_preferences(preferences)
        elif diet_preference == 'Ketogenic':
            if not preferences.ketogenic:
                reset_diet_preferences(preferences)
                preferences.ketogenic = True
            else:
                reset_diet_preferences(preferences)
        elif diet_preference == 'Dairy Free':
            if not preferences.dairy_free:
                reset_diet_preferences(preferences)
                preferences.dairy_free = True
            else:
                reset_diet_preferences(preferences)
        elif diet_preference == 'Gluten Free':
            if not preferences.gluten_free:
                reset_diet_preferences(preferences)
                preferences.gluten_free = True
            else:
                reset_diet_preferences(preferences)

        if preferences.save():
            print("saved")
        else:
            print("not saved")

    return redirect('/')


def search_recipe_by_ingredients(request):
    quota_reached = False
    recipe_dictionary = []

    if request.method == 'GET':
        selected_ingredients = request.session['clicked_ingredients']

        if selected_ingredients:
            selected_ingredients_string = ",".join(map(lambda recipe_title: str(recipe_title), selected_ingredients))

            recipe_list = []

            if request.user.is_authenticated and DietPreference.objects.filter(
                    custom_user_id=request.user.id).first():
                diet_preference = get_diet_preferences(request.user.id)

                if diet_preference != '':
                    recipe_list = settings.SPOONACULAR_API.search_recipes_complex(
                        includeIngredients=selected_ingredients_string, diet=diet_preference, number=12).json().get(
                        'results')
                else:
                    recipe_list = settings.SPOONACULAR_API.search_recipes_by_ingredients(
                        ingredients=selected_ingredients_string, number=12).json()
            else:
                recipe_list = settings.SPOONACULAR_API.search_recipes_by_ingredients(
                    ingredients=selected_ingredients_string, number=12).json()

            if recipe_list is not None and 'status' not in recipe_list:
                recipe_dictionary = list(map(lambda recipe_dict: {
                    'title': recipe_dict.get('title'),
                    'vegan': recipe_dict.get('vegan'),
                    'img': 'https://spoonacular.com/recipeImages/{}-556x370.jpg'.format(recipe_dict.get('id')),
                    'extendedIngredients': recipe_dict.get('extendedIngredients'),
                    'id': recipe_dict.get('id')
                }, recipe_list))
            else:
                quota_reached = True
        else:
            if settings.QUOTA_REACHED:
                quota_reached = True
            else:
                if request.user.is_authenticated and DietPreference.objects.filter(custom_user_id=request.user.id).first():
                    if get_diet_preferences(request.user.id) != '':
                        recipe_dictionary = filter_recipes_by_diet(request.user.id, settings.RECIPELIST)
                    else:
                        recipe_dictionary = settings.RECIPELIST

    user_saved_recipes = SavedRecipe.objects.filter(custom_user_id=request.user.id)

    html = render_to_string('recipe_container.html',
                        {'recipes': recipe_dictionary, 'saved_recipes': user_saved_recipes, 'user': request.user,
                         'quota_reached': quota_reached})
    return HttpResponse(html)


def ingredient_search(request):
    if request.method == 'GET':
        ingredient = request.GET.get('ingredient')
        ingredient_dict_items = settings.INGREDIENTS_DICT.items
        ingredient = ingredient.lower()
        if ingredient == '':
            response = render_to_string('_sidebar_ingredient_categories.html',
                                        {'ingredient_dict': ingredient_dict_items})
            return HttpResponse(response)
        else:
            ingredient_list = []
            for keys, values in settings.INGREDIENTS_DICT.items():
                [ingredient_list.append(i) for i in values if i != '']

            matchedIngredients = [searched_ingredient for searched_ingredient in ingredient_list if
                                  ingredient in searched_ingredient]
            response = render_to_string('_search_sidebar_ingredient.html', {'searched_ingredients': matchedIngredients})

            return HttpResponse(response)


def update_ingredient_filter(request):
    if request.method == 'GET':
        clickedIngredient = request.GET.get('clicked_ingredient')

        if 'clicked_ingredients' not in request.session:
            request.session['clicked_ingredients'] = []

        clicked_ingredients_list = request.session['clicked_ingredients']

        if clickedIngredient in clicked_ingredients_list:
            clicked_ingredients_list.remove(clickedIngredient)

            if not clicked_ingredients_list:
                response = HttpResponse()
                response.status_code = 403

                request.session['clicked_ingredients'] = clicked_ingredients_list
                return response
        else:
            clicked_ingredients_list.append(clickedIngredient)

        request.session['clicked_ingredients'] = clicked_ingredients_list

    html = render_to_string('_selected_ingredients.html', {'selectedIngredients': clicked_ingredients_list})
    return HttpResponse(html)


def recipe_query(request):
    quota_reached = False
    global saved_recipes
    recipe_list = []

    recipe_dictionary = []

    if request.method == 'GET':
        recipe = request.GET.get('query_recipe')

        if request.user.is_authenticated and DietPreference.objects.filter(
                custom_user_id=request.user.id).first():

            diet_preference = ''
            preferences_object = DietPreference.objects.get(pk=request.user.id)

            if preferences_object.vegan:
                diet_preference = 'vegan'
            elif preferences_object.vegetarian:
                diet_preference = 'vegetarian'
            elif preferences_object.ketogenic:
                diet_preference = 'ketogenic'
            elif preferences_object.dairy_free:
                diet_preference = 'dairy_free'
            elif preferences_object.gluten_free:
                diet_preference = 'gluten_free'

            if diet_preference != '':
                recipe_list = settings.SPOONACULAR_API.search_recipes_by_name(query=recipe,
                                                                              diet=diet_preference).json().get(
                    'results')
            else:
                recipe_list = settings.SPOONACULAR_API.search_recipes_by_name(query=recipe, diet=search_preferences(
                    request.user.id)).json().get('results')
        else:
            recipe_list = settings.SPOONACULAR_API.search_recipes_by_name(query=recipe, diet=search_preferences(
                request.user.id)).json().get('results')

    if recipe == '' or recipe is None:
        recipe_dictionary = settings.RECIPELIST
        quota_reached = settings.QUOTA_REACHED
    else:
        saved_recipes = SavedRecipe.objects.filter(custom_user_id=request.user.id)

        # Removing Recipes without an Image (Spoonacular Bug)
        for recipe in recipe_dictionary:
            if recipe.get('img') is None:
                recipe_dictionary.remove(recipe)

        if recipe_list is not None:
            recipe_dictionary = list(map(lambda recipe_dict: {
                'title': recipe_dict.get('title'),
                'img': f"https://spoonacular.com/recipeImages/{recipe_dict.get('image')}",
                'id': recipe_dict.get('id')
            }, recipe_list))
        else:
            quota_reached = True

    user_saved_recipes = SavedRecipe.objects.filter(custom_user_id=request.user.id)

    recipe_list = recipe_dictionary

    html = render_to_string('recipe_container.html',
                            {'recipes': recipe_list, 'saved_recipes': user_saved_recipes, 'user': request.user, 'quota_reached': quota_reached})

    return HttpResponse(html)


def recipe_view(request, recipeId):
    register_form = RegisterForm()
    login_form = AuthenticationForm()
    global saved
    saved = False
    recipe_id = 0
    rawRecipe = settings.SPOONACULAR_API.get_recipe_information(id=recipeId).json()

    recipeInfo = {}

    keys = ['id', 'title', 'vegetarian', 'glutenFree', 'dairyFree',
            'dairyFree', 'vegan', 'veryHealthy', 'preparationMinutes',
            'cookingMinutes', 'extendedIngredients', 'servings',
            'image', 'summary', 'analyzedInstructions']
    for key in keys:
        if key in rawRecipe:
            if key == 'spoonacularScore':
                a = (rawRecipe['spoonacularScore'] // 10) * 10
                # Larger multiple
                b = a + 10
                rating = b / 10 if rawRecipe['spoonacularScore'] - a > b - rawRecipe['spoonacularScore'] else a / 10;
                recipeInfo['ratingStars'] = range(0, int(rating))
                recipeInfo['remainderStars'] = range(0, int(10 - rating))
            elif key == 'analyzedInstructions' and rawRecipe['analyzedInstructions'] != []:
                recipeInfo['analyzedInstructions'] = rawRecipe['analyzedInstructions'][0]['steps']
            else:
                recipeInfo[key] = rawRecipe[key]

    spoonacular_id = recipeInfo['id']

    if request.user.is_authenticated:
        user_saved_recipes = SavedRecipe.objects.filter(custom_user_id=request.user.id)
        for recipe in user_saved_recipes:
            if recipe.recipe_id == recipeInfo['id']:
                saved = True
                recipe_id = recipe.id

    return render(request, 'recipepage.html', {'recipe': recipeInfo,
                                               'saved': saved,
                                               'id': recipe_id,
                                               'spoonacular_id': spoonacular_id, 'register_form': register_form, 'login_form': login_form})


def update_twitter_feed(request):
    tweet_status_object = []

    try:
        for tweet in tweepy.Cursor(settings.TWITTER_API.search, q='@chefitup6', rpp=100).items(100):
            tweet_status_object.append(tweet)

        json_tweets = map(lambda t: t._json, tweet_status_object)

        TWEET_LIST = list(map(lambda tweet_dict: {
            'text': tweet_dict.get('text').lower().replace('@chefitup6', '').capitalize(),
            'profile_img': (tweet_dict.get('user').get('profile_image_url')).replace('http','https'),
            'name': tweet_dict.get('user').get('screen_name'),
            "tweet_url": f"https://twitter.com/{tweet_dict.get('user').get('screen_name')}/status/{tweet_dict.get('id')}"
        }, json_tweets))
    except tweepy.errors.TweepyException:
        response = HttpResponse()
        response.status_code = 403
        return response

    response = render_to_string('_twitter_feed.html', {'tweets': TWEET_LIST})
    return HttpResponse(response)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        login_form = AuthenticationForm(request=request, data=request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                if not DietPreference.objects.filter(pk=user.id).first():
                    DietPreference.objects.create(custom_user_id=user.id, dairy_free=0, vegetarian=0, vegan=0, gluten_free=0, ketogenic=0)
                    
                return redirect('/')
            else:
                response = HttpResponse()
                response.status_code = 403
                return response

    response = HttpResponse()
    response.status_code = 403
    return response


def home_view(request):
    # collab_recommender = turicreate_recommender.CollaborativeRecommender.get_instance()
    suggested_recipes = []

    # Popular Recipes Fetching
    suggested_recipes_ids = recommendations.get_random_top_recipes(2)

    if request.user.is_authenticated:
        pass
        # collab_recipe_ids = collab_recommender.get_recommendations(user_id=request.user.id, n=2)
        # suggested_recipes_ids.extend(collab_recipe_ids)

    if len(suggested_recipes_ids) > 0:
        recipes_string = ",".join(map(lambda recipe_id: str(recipe_id), suggested_recipes_ids))
        recipes_info = settings.SPOONACULAR_API.get_recipe_information_bulk(ids=recipes_string)

        # if the result is a json object with failure status and not a list with recipes
        # do not try fill the convert this response to recipe list and leave suggested_recipes empty
        # it will not display any suggestions but will prevent the page from breaking
        if recipes_info.status_code == 200:
            suggested_recipes = settings.SPOONACULAR_API.convert_to_dict(recipes_info.json())

    request.session['clicked_ingredients'] = []
    global saved_recipes

    preferences = []
    register_form = RegisterForm()
    login_form = AuthenticationForm()

    tweetlist = settings.TWEET_LIST

    saved_recipes = SavedRecipe.objects.filter(custom_user_id=request.user.id)

    # check if user exists and checks if user has an associated diet preference set.
    if request.user.is_authenticated and DietPreference.objects.filter(custom_user_id=request.user.id).first():
        preferences = DietPreference.objects.get(pk=request.user.id)

        if get_diet_preferences(request.user.id) != '':
            recipes_displayed = filter_recipes_by_diet(request.user.id, settings.RECIPELIST)
        else:
            recipes_displayed = settings.RECIPELIST
    else:
        recipes_displayed = settings.RECIPELIST

    recipes = recipes_displayed

    context = {
        "quota_reached": settings.QUOTA_REACHED,
        "preferences": preferences,
        "saved_recipes": saved_recipes,
        "login_form": login_form,
        "register_form": register_form,
        "recipes": recipes,
        "suggestions": suggested_recipes,
        "tweets": tweetlist,
        "INGREDIENTS_DICT": {
            "Dairy": ["salted butter", "unsalted butter", "margarine", "egg", "skimmed milk", "whole milk",
                      "semi-skimmed milk", "parmesan", "cheddar", "american cheese", "sour cream", "cream cheese",
                      "mozzarella", "yogurt", "double cream", "single cream", "evaporated milk", "whipped cream",
                      "half and half", "feta", "monterey jack cheese", "condensed milk", "cottage cheese", "ice cream",
                      "swiss cheese", "velveeta", "frosting", "buttermilk", "ricotta", "goat cheese", "provolone",
                      "blue cheese", "powdered milk", "colby cheese", "pepper jack", "italian cheese", "soft cheese",
                      "gouda", "pepperjack cheese", "romano", "brie", "pizza cheese", "ghee", "creme fraiche",
                      "cheese soup", "guyere", "pecorino cheese", "custard", "muenster", "queso fresco cheese",
                      "hard cheese", "havarti cheese", "asiago", "mascarpone", "neufchatel", "halloumi", "paneer",
                      "brick cheese", "camembert cheese", "goat milk", "garlic herb cheese", "edam cheese", "manchego",
                      "fontina", "stilton cheese", "emmenthaler cheese", "red leicester cheese", "jarlsberg cheese",
                      "bocconcini cheese", "farmer cheese", "creme de cassis", "wensleydale cheese", "longhorn cheese",
                      "double gloucester cheese", "raclette cheese", "lancashire cheese", "cheshire cheese"],
            "Vegetables": ["onion", "garlic", "tomato", "potato", "carrot", "bell pepper", "basil", "parsley",
                           "broccoli", "sweetcorn", "spinach", "mushroom", "green beans", "ginger", "red chili pepper",
                           "green chili pepper", "celery", "rosemary", "salad greens", "red onion", "cucumber",
                           "sweet potato", "pickle", "avocado", "zucchini", "cilantro", "frozen vegetables", "olive",
                           "asparagus", "cabbage", "cauliflower", "dill", "kale", "mixed vegetable", "pumpkin",
                           "squash", "mint", "scallion", "sun dried tomato", "shallot", "eggplant", "beetroot",
                           "butternut squash", "horseradish", "leek", "caper", "brussels sprout", "artichoke heart",
                           "chia seeds", "radish", "sauerkraut", "artichoke", "portobello mushrooms", "weet pepper",
                           "arugula", "spaghetti squash", "capsicum", "bok choy", "parsnip", "okra", "yam", "fennel",
                           "turnip", "snow peas", "bean sprouts", "seaweed", "chard", "collard", "canned tomato",
                           "pimiento", "watercress", "tomatillo", "rocket", "mustard greens", "bamboo shoot",
                           "rutabaga", "endive", "broccoli rabe", "jicama", "kohlrabi", "hearts of palm", "butternut",
                           "celery root", "daikon", "radicchio", "porcini", "chinese broccoli", "jerusalem artichoke",
                           "cresswater chestnut", "dulsemicro greens", "burdock", "chayote"],
            "Fruit": ["lemon", "apple", "banana", "lime", "strawberry", "orange", "pineapple", "blueberry", "raisin",
                      "coconut", "grape", "peach", "raspberry", "cranberry", "mango", "pear", "blackberry", "cherry",
                      "date", "watermelon", "berries", "kiwi", "grapefruit", "mandarin", "craisins", "cantaloupe",
                      "plum", "apricot", "clementine", "prunes", "apple butter", "pomegranate", "nectarine", "fig",
                      "tangerine", "papaya", "rhubarb", "sultanas", "plantain", "currant", "passion fruit", "guava",
                      "persimmons", "lychee", "lingonberry", "tangelos", "kumquat", "boysenberry", "star fruit",
                      "quince", "honeydew", "crabapples"],
            "Baking": ["rice", "pasta", "flour", "bread", "baking powder", "baking soda", "bread crumbs", "cornstarch",
                       "rolled oats", "noodle", "flour tortillas", "pancake mix", "yeast", "cracker", "quinoa",
                       "brown rice", "cornmeal", "self raising flour", "cake mix", "saltines", "popcorn",
                       "macaroni cheese mix", "corn tortillas", "ramen", "cereal", "biscuits", "stuffing mix",
                       "couscous", "pie crust", "bisquick", "chips", "angel hair", "coconut flake", "bread flour",
                       "croutons", "lasagne", "pizza dough", "bagel", "puff pastry", "hot dog bun", "barley",
                       "multigrain bread", "potato flakes", "pretzel", "cornbread", "english muffin", "cornflour",
                       "crescent roll dough", "cream of wheat", "coconut flour", "pita", "risotto", "muffin mix",
                       "bicarbonate of soda", "ravioli", "wheat", "rice flour", "polenta", "baguette", "gnocchi",
                       "vermicelli", "semolina", "wheat germ", "buckwheat", "croissants", "bread dough", "filo dough",
                       "yeast flake", "pierogi", "matzo meal", "rye", "tapioca flour", "shortcrust pastry",
                       "potato starch", "breadsticks", "ciabatta", "spelt", "angel food", "tapioca starch", "starch",
                       "whole wheat flour", "gram flour", "sourdough starter", "wafer", "bran", "challah",
                       "sponge cake", "malt extract", "sorghum flour"],
            "Sweeteners": ["granulated sugar", "brown sugar", "caster sugar", "honey", "confectioners sugar",
                           "maple syrup", "golden syrup", "corn syrup", "molasses", "artificial sweetener",
                           "agave nectar"],
            "Spices": ["cinnamon", "vanilla extract", "vanilla powder", "garlic powder", "paprika", "smoked paprika",
                       "oregano", "chili powder", "red pepper flake", "cumin", "cayenne", "italian seasoning", "thyme",
                       "onion powder", "nutmeg", "ground nutmeg", "curry powder", "bay leaf", "taco seasoning", "sage",
                       "clove", "allspice", "turmeric", "chive", "pepper", "corn", "ground coriander",
                       "cajun seasoning", "coriander", "celery salt", "herbs", "steak seasoning", "poultry seasoning",
                       "chile powder", "cardamom", "italian herbs", "tarragon", "garam masala", "marjoram",
                       "mustard seed", "celery seed", "chinese five spice", "italian spice", "saffron", "onion flake",
                       "herbes de provence", "chipotle", "dill seed", "fennel seed", "caraway", "cacao", "star anise",
                       "savory", "chili paste", "tamarind", "aniseed", "fenugreek", "lavender", "old bay seasoning",
                       "lemon balm"],
            "Meats": ["chicken breast", "ground beef", "bacon", "sausage", "beef steak", "ham", "hot dog", "pork chops",
                      "chicken thighs", "ground turkey", "cooked chicken", "turkey", "pork", "pepperoni",
                      "whole chicken", "chicken leg", "ground pork", "chorizo", "chicken wings", "beef roast",
                      "polish sausage", "salami", "pork roast", "ground chicken", "pork ribs", "spam", "venison",
                      "pork shoulder", "bologna", "bratwurst", "prosciutto", "lamb", "corned beef", "chicken roast",
                      "lamb chops", "pancetta", "ground lamb", "beef ribs", "duck", "pork belly", "beef liver",
                      "leg of lamb", "canadian bacon", "beef shank", "veal", "chicken giblets", "cornish hen",
                      "lamb shoulder", "lamb shank", "deer", "ground veal", "pastrami", "rabbit", "sliced turkey",
                      "pork loin", "elk", "beef suet", "veal cutlet", "lamb loin", "marrow bones", "goose",
                      "chicken tenders", "veal chops", "quail", "oxtail", "pheasant", "lamb liver", "moose",
                      "turkey liver", "pork liver", "veal shank", "foie gras", "beef sirloin", "liver sausage",
                      "sweetbread", "wild boar", "snail", "pigeon", "duck liver", "goose liver", "grouse", "ostrich",
                      "soppressata", "alligator"],
            "Fish": ["canned tuna", "salmon", "tilapia", "fish fillets", "cod", "canned salmon", "anchovy",
                     "smoked salmon", "sardines", "tuna steak", "whitefish", "halibut", "trout", "haddock", "flounder",
                     "catfish", "mahi mahi", "mackerel", "sole", "sea bass", "red snapper", "swordfish", "pollock",
                     "herring", "perch", "grouper", "caviar", "monkfish", "rockfish", "lemon sole", "pike",
                     "barramundi", "eel", "bluefish", "carp", "cuttlefish", "pompano", "arctic char", "john dory",
                     "marlin", "amberjack", "sturgeon"],
            "Seafood": ["shrimp", "crab", "prawns", "scallop", "clam", "lobster", "mussel", "oyster", "squid",
                        "calamari", "crawfish", "octopus", "cockle", "conch", "sea urchin"],
            "Condiments": ["mayonnaise", "ketchup", "mustard", "vinegar", "soy sauce", "balsamic vinegar",
                           "worcestershire", "hot sauce", "barbecue sauce", "ranch dressing", "wine vinegar",
                           "apple cider vinegar", "cider vinegar", "italian dressing", "rice vinegar", "salad dressing",
                           "tabasco", "fish sauce", "teriyaki", "steak sauce", "tahini", "enchilada sauce",
                           "vinaigrette dressing", "oyster sauce", "honey mustard", "sriracha", "caesar dressing",
                           "taco sauce", "mirin", "blue cheese dressing", "sweet and sour sauce", "thousand island",
                           "picante sauce", "buffalo sauce", "french dressing", "tartar sauce", "cocktail sauce",
                           "marsala", "adobo sauce", "tzatziki sauce", "sesame dressing", "ponzu", "duck sauce",
                           "pickapeppa sauce", "yuzu juice", "cream sauce"],
            "Oils": ["olive oil", "vegetable oil", "cooking spray", "canola oil", "shortening", "sesame oil",
                     "coconut oil", "peanut oil", "sunflower oil", "lard", "grape seed oil", "corn oil", "almond oil",
                     "avocado oil", "safflower oil", "walnut oil", "hazelnut oil", "palm oil", "soybean oil",
                     "mustard oil", "pistachio oil", "soya oil"],
            "Seasonings": ["bouillon", "ground ginger", "sesame seed", "cream of tartar", "chili sauce", "soya sauce",
                           "apple cider", "hoisin sauce", "liquid smoke", "rice wine", "vegetable bouillon",
                           "poppy seed", "balsamic glaze", "miso", "wasabi", "fish stock", "rose water",
                           "pickling salt", "champagne vinegar", "bbq rub", "jamaican jerk spice", "accent seasoning",
                           "pickling spice", "mustard powder", "mango powder", "adobo seasoning", "kasuri methi",
                           "caribbean jerk seasoning", "brine", "matcha powder", "cassia"],
            "Sauces": ["tomato sauce", "tomato paste", "salsa", "pesto", "alfredo sauce", "beef gravy", "curry paste",
                       "chicken gravy", "cranberry sauce", "turkey gravy", "mushroom gravy", "sausage gravy",
                       "onion gravy", "cream gravy", "pork gravy", "tomato gravy", "giblet gravy"],
            "Legumes": ["green beans", "peas", "black beans", "chickpea", "lentil", "refried beans", "hummus",
                        "chili beans", "lima beans", "kidney beans", "pinto beans", "edamame", "split peas",
                        "snap peas", "soybeans", "cannellini beans", "navy beans", "french beans", "red beans",
                        "great northern beans", "fava beans"],
            "Alcohol": ["white wine", "beer", "red wine", "vodka", "rum", "whiskey", "tequila", "sherry", "bourbon",
                        "cooking wine", "whisky", "liqueur", "brandy", "gin", "kahlua", "irish cream", "triple sec",
                        "champagne", "amaretto", "cabernet sauvignon", "vermouth", "bitters", "maraschino", "sake",
                        "grand marnier", "masala", "dessert wine", "schnapps", "port wine", "sparkling wine", "cognac",
                        "chocolate liqueur", "burgundy wine", "limoncello", "creme de menthe", "bloody mary",
                        "raspberry liquor", "curacao", "frangelico", "shaoxing wine", "absinthe", "madeira wine",
                        "ouzo", "anisette", "grappa", "ciclon", "drambuie"],
            "Soup": ["chicken broth", "mushroom soup", "beef broth", "tomato soup", "vegetable stock", "chicken soup",
                     "onion soup", "vegetable soup", "celery soup", "dashi", "lamb stock", "pork stock", "veal stock"],
            "Nuts": ["peanut butter", "almond", "walnut", "pecan", "peanut", "cashew", "flax", "pine nut", "pistachio",
                     "almond meal", "hazelnut", "macadamia", "almond paste", "chestnut", "praline", "macaroon"],
            "Dairy_Alternatives": ["coconut milk", "almond milk", "soy milk", "rice milk", "hemp milk",
                                   "non dairy creamer"],
            "Desserts": ["chocolate", "apple sauce", "strawberry jam", "graham cracker", "marshmallow",
                         "chocolate syrup", "potato chips", "nutella", "chocolate morsels", "bittersweet chocolate",
                         "pudding mix", "raspberry jam", "dark chocolate", "chocolate chips", "jam", "white chocolate",
                         "brownie mix", "chocolate pudding", "jello", "caramel", "chocolate powder", "candy",
                         "corn chips", "cookies", "apricot jam", "chocolate bar", "cookie dough", "oreo", "doritos",
                         "chocolate cookies", "butterscotch", "blackberry preserves", "blueberry jam",
                         "peach preserves", "cherry jam", "fig jam", "plum jam", "cinnamon roll", "fudge",
                         "cookie crumb", "grape jelly", "chilli jam", "lady fingers", "black pudding",
                         "chocolate wafer", "gummy worms", "biscotti biscuit", "doughnut", "amaretti cookies",
                         "apple jelly", "red pepper jelly", "orange jelly", "jalapeno jelly", "mint jelly",
                         "currant jelly", "lemon jelly", "quince jelly"],
            "Beverages": ["coffee", "orange juice", "tea", "green tea", "apple juice", "tomato juice", "cola",
                          "chocolate milk", "pineapple juice", "lemonade", "cranberry juice", "espresso", "fruit juice",
                          "ginger ale", "club soda", "grenadine", "margarita mix", "cherry juice"]}

    }

    return render(request, 'contentpage.html', context)


@csrf_exempt
def save_recipe(request):
    redirect_id = literal_eval(request.POST.get('redirect_id'))

    if request.method == "POST":
        if request.user.is_authenticated:

            current_user = request.user

            id = literal_eval(request.POST.get('id'))

            user_saved_recipes = SavedRecipe.objects.filter(custom_user_id=current_user.id, recipe_id=id)
            if not (user_saved_recipes.count() >= 1):
                recipe_save = SavedRecipe(custom_user_id=current_user.id, recipe_id=id)
                recipe_save.save()

                # Update simple recommender table
                updater.update_popular_table(recipe_id=id, favourite=True)

                # Update collaborative recommender
                # collab_recommender = turicreate_recommender.CollaborativeRecommender.get_instance()
                # collab_recommender.update_recommender_model()

                messages.success(request, "Recipe saved successfully", extra_tags="thumbs-up")
            else:
                messages.info(request, "You have already saved this recipe")

            return redirect('/recipe/{id}'.format(id=redirect_id))
        else:
            messages.warning(request, "You must be logged in to save a recipe")
            return redirect('/recipe/{id}'.format(id=redirect_id))


@csrf_exempt
def unsave_recipe(request):
    redirect_id = literal_eval(request.POST.get('redirect_id'))

    if request.method == "POST":
        if request.user.is_authenticated:
            current_user = request.user

            id = literal_eval(request.POST.get('id'))

            SavedRecipe.objects.filter(id=id).delete()

            # Update simple recommender table
            updater.update_popular_table(recipe_id=id, favourite=False)

            # Update collaborative recommender
            # collab_recommender = turicreate_recommender.CollaborativeRecommender.get_instance()
            # collab_recommender.update_recommender_model()

            messages.success(request, "Recipe unsaved successfully")
            return redirect('/recipe/{id}'.format(id=redirect_id))
    else:
        messages.warning(request, "You must be logged in to unsave a recipe")
        return redirect('/recipe/{id}'.format(id=redirect_id))


def convert_to_dict(reduced_list):
    RECIPELIST = list(map(lambda recipe_dict: {
        'title': recipe_dict.get('title'),
        'vegan': recipe_dict.get('vegan'),
        'id': recipe_dict.get('id'),
        'img': 'https://spoonacular.com/recipeImages/{}-556x370.jpg'.format(recipe_dict.get('id')),
    }, reduced_list))

    return RECIPELIST


def filter_recipes_by_diet(user_id, recipes):
    diet_preference = ''
    preferences_object = DietPreference.objects.get(pk=user_id)

    if preferences_object.vegan:
        diet_preference = 'vegan'
    elif preferences_object.vegetarian:
        diet_preference = 'vegetarian'
    elif preferences_object.ketogenic:
        diet_preference = 'ketogenic'
    elif preferences_object.dairy_free:
        diet_preference = 'dairy_free'
    elif preferences_object.gluten_free:
        diet_preference = 'gluten_free'

    filtered_recipe_list = []

    for recipe in recipes:
        if recipe.get(diet_preference):
            filtered_recipe_list.append(recipe)

    return filtered_recipe_list


def get_diet_preferences(user_id):
    preferences_object = DietPreference.objects.get(pk=user_id)

    if preferences_object.vegan:
        diet_preference = 'vegan'
    elif preferences_object.vegetarian:
        diet_preference = 'vegetarian'
    elif preferences_object.ketogenic:
        diet_preference = 'ketogenic'
    elif preferences_object.dairy_free:
        diet_preference = 'dairy_free'
    elif preferences_object.gluten_free:
        diet_preference = 'gluten_free'
    else:
        diet_preference = ''

    return diet_preference


def send_tweet(request):
    if request.method == 'POST':
        page_id = request.POST['recipe_id']
        tweet = request.POST['message']

        try:
            formatted_tweet = f'@ChefItUp6 Tweet Shared by our User {request.user.username}: {tweet}'
            settings.TWITTER_API.update_status(status=formatted_tweet)
            messages.success(request, "Successfully submitted tweet.", extra_tags="thumbs-up")
            return redirect('/')
        except:
            messages.error(request, "Failed to submit the tweet.")
            return redirect('/')

# Displays recipes in order of the users preferences
def check_user_diet_preferences(user_id, recipes):
    # get user's saved preferences
    data = get_preferences(user_id)
    recipe_filtered_preferences = []
    keys = ['vegan', 'vegetarian', 'gluten_free', 'ketogenic', 'dairy_free']

    for i in range(len(recipes)):

        num_prefs = 0
        for key in keys:
            # if 1 of the keys criteria match to the user preferences add it to items to be returned to user.
            if recipes[i][key] == data[key]:
                num_prefs += 1
        # adds the number of preferences a recipe fulfils of the user's criteria
        recipes[i]["num_preferences"] = num_prefs
        recipe_filtered_preferences.append(recipes[i])
    # Order recipe from highest num_prefs to lowest
    recipe_filtered_preferences = sorted(recipe_filtered_preferences, key=lambda recipe: recipe["num_preferences"],
                                         reverse=True)
    return recipe_filtered_preferences


# turns user preferences into a string for request
def search_preferences(user_id):
    query = []
    if get_preferences(user_id) is not None:
        for key, value in get_preferences(user_id).items():
            if value == 1:
                query.append(key)

        if not query:
            return ""
        else:
            return ",".join(query)
    else:
        return ""


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if form.save():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                
                if not DietPreference.objects.filter(pk=user.id).first():
                    DietPreference.objects.create(custom_user_id=user.id, dairy_free=0, vegetarian=0, vegan=0, gluten_free=0, ketogenic=0)
                
                response = HttpResponse()
                response.status_code = 403
                return response
        else:
            response = render(request, '_register_form.html', {'register_form': form})
            return response


def preference(request):
    if request.method == "POST":
        preference_form = DietPreferenceForm(request.POST)
        if preference_form.is_valid():
            preference = preference_form.save(commit=False)
            preference.custom_user = request.user
            preference.save()
