import django
from django.db import models


class PopularRecipe(models.Model):
    recipe_id = models.IntegerField()
    fav_count = models.IntegerField()

    objects = models.Manager()

    class Meta:
        ordering = ["-fav_count"]
        indexes = [
            models.Index(fields=['-fav_count'])
        ]

    def __str__(self):
        return str(self.recipe_id) + " - " + str(self.fav_count)
