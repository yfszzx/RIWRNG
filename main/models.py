from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth.models import User

class user(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    openid  = models.CharField(unique=True, null=False, max_length=100)
    nickname = models.CharField(null=True, max_length=200)
    sex = models.BooleanField(default=False) 
    headimgurl = models.CharField(null=True, max_length=1000)
    grade = models.SmallIntegerField(null=True, default=0)

class score(models.Model):
    user = models.OneToOneField(user, primary_key=True, on_delete=models.CASCADE)
    train_num = models.BigIntegerField(null=True, default=0)
    train_score = models.BigIntegerField(null=True, default=0)
    verify_num = models.BigIntegerField(null=True, default=0)
    verify_score = models.BigIntegerField(null=True, default=0)
    exp_num = models.BigIntegerField(null=True, default=0)
    exp_score = models.BigIntegerField(null=True, default=0)
    latest_exp_time =  models.DateTimeField(null=True, default=timezone.now) 


class experiment(models.Model):
    user = models.ForeignKey(user, db_index=True, on_delete=models.CASCADE)
    exp_mod =  models.CharField(null=True, max_length=1) # 't': train , 'v':verify, 'e':experiment
    rnd_num = models.SmallIntegerField(null=True, default=0)
    exp_score = models.SmallIntegerField(null=True, default=0)
    compare_score = models.SmallIntegerField(null=True, default=0)
    research_score = models.SmallIntegerField(null=True, default=0)
    create_timestamp = models.DateTimeField(auto_now_add=True) 



