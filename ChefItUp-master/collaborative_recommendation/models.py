from django.db import models


class SimilarUser(models.Model):
    user_id = models.IntegerField()
    similar_user_id = models.IntegerField()

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['user_id'])
        ]

    def __str__(self):
        return str(self.user_id) + " - " + str(self.similar_user_id)
