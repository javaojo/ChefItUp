from django import forms

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm


from .models import CustomUser, DietPreference


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ('oldpassword', 'newpass', 'newpass2')


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].help_text = None

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class UpdateProfile(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')


class DietPreferenceForm(forms.ModelForm):
    class Meta:
        model = DietPreference
        fields = ('ketogenic', 'dairy_free', 'vegetarian', 'vegan', 'gluten_free',)
