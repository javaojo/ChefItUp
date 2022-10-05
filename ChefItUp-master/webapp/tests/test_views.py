from django.test import TestCase, Client
from django.urls import reverse

from users.models import SavedRecipe, CustomUser, DietPreference
from webapp.views import *
from mock import Mock



class TestView(TestCase):
    "Testing webapp views"

    def setUp(self):
        self.client = Client()

        self.user1 = CustomUser.objects.create(
            username="ChefItUp2020",
            first_name="John",
            last_name="Doe",
            email="chefitup@gmail.com"
        )
        self.user1.set_password('chefitup2020')

        self.preference1=DietPreference.objects.create(
            custom_user_id=1, dairy_free=1,
            vegetarian=1, vegan=0,gluten_free=0,
            ketogenic=0
        )

        self.user1.save()

    def tearDown(self):
        del self.user1
        del self.preference1

    def test_unsuccessful_profile_view(self):
        """
            Testing users not logged in cannot access profile page
            get redirected to homepage
        """
        response = self.client.get(reverse('profile'), follow=True)
        self.assertTemplateUsed(response, 'contentpage.html')

    def test_successful_profile_view(self):
        "Testing logged in users can access their profile page"
        user_login = self.client.login(username="ChefItUp2020", password="chefitup2020")
        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_view_exists(self):
        "Testing that all users can access home page"
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contentpage.html')

    def test_successful_user_login(self):
        "Testing correct user login"
        user_login = self.client.login(username="ChefItUp2020", password="chefitup2020")
        self.assertTrue(user_login)

    def test_unsuccessful_user_login(self):
        "Incorrect password login test"
        user_login = self.client.login(username="ChefItUp2020", password="Wrong_Password")
        self.assertFalse(user_login)

    def test_user_login_on_homepage(self):

        user_login = self.client.login(username="ChefItUp2020", password="chefitup2020")
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.context['user'].username, 'ChefItUp2020')

    def test_search_prefereces(self):
        "Testing function returns selected preferences as a string"
        user_login = self.client.login(username="ChefItUp2020", password="chefitup2020")
        self.assertEqual(search_preferences(1), "dairy_free,vegetarian")

    def test_invalid_login_user(self):
        "Testing invalid login returns 403"
        request = Mock(session={'username': "hi", "password": "124WADCCu!"}, method='POST')
        self.assertEqual(login_user(request).status_code, 403)