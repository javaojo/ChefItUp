from ChefItUp import settings
from ChefItUp.spoonacular_utils.api import API

SPOONACULAR_API_KEY = settings.SPOONACULAR_API_KEY

def setUp(self):
    self.api = API(SPOONACULAR_API_KEY)

# Search by name
def search_by_name(request, self):
    pass
    #response = self.api.search_recipes_by_name(query, )
    #data = response.json()
    #print(data[0]['name'])