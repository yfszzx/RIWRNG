from django.db import models

class user(models.Model):
    name = models.CharField(null=True, max_length=100)

class experiment(models.Model):
    user = models.ForeignKey(user, db_index=True, on_delete=models.CASCADE)
    num = models.SmallIntegerField(null=True, default=0)



