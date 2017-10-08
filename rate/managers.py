from django.db import models


class RateManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)