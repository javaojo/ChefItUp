from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = (models.CharField(max_length=254))
    username = models.CharField(max_length=30, unique=True)
    password = (models.CharField(max_length=254))
    first_name = (models.CharField(max_length=254))
    last_name = (models.CharField(max_length=254))


class DietPreference(models.Model):
    custom_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    dairy_free = (models.BooleanField("dairy free", default=False))
    vegetarian = (models.BooleanField("vegetarian", default=False))
    vegan = (models.BooleanField("vegan", default=False))
    gluten_free = (models.BooleanField("gluten free", default=False))
    ketogenic = (models.BooleanField("ketogenic", default=False))


class SavedRecipe(models.Model):
    id = models.AutoField(primary_key=True)
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe_id = models.IntegerField(default=False)

    class Meta:
        db_table = 'users_savedrecipe'
        constraints = [
            models.UniqueConstraint(fields=['recipe_id', 'custom_user'], name='unique_favourited')
        ]
