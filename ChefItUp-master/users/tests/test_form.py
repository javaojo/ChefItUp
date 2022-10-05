from django.test import TestCase
from users import forms

class MyTests(TestCase):

    def test_diet_preference_form(self):
        form_data = {'ketogenic': True, 'dairy_free': False,
            'vegetarian': True, 'vegan': False,
            'gluten_free': False}

        form = forms.DietPreferenceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_register_form(self):

        "Invalid register form"
        form_data = {'username': "", 'first_name': "",
                     'last_name': "", 'email': "",
                     'password1': "", 'password2': ""}

        form = forms.RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_register_form(self):

        "valid register form"
        form_data = {'username': "User1", 'first_name': "Jane",
                     'last_name': "Doe", 'email': "example@gmail.com",
                     'password1': "tHiSisatestpassword!*hi", 'password2': "tHiSisatestpassword!*hi"}

        form = forms.RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

