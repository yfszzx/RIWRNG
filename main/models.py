from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth.models import AbstractUser

class userInfo(AbstractUser):
    #user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    #openid  = models.CharField(unique=True, null=False, max_length=100)
    nid = models.AutoField(primary_key=True)
    nickname = models.CharField(null=True, max_length=200)
    sex = models.SmallIntegerField(null=True, default=0)
    headimgurl = models.CharField(null=True, max_length=1000)
    grade = models.SmallIntegerField(null=True, default=0)
    direction = models.BooleanField(default=True) 

class total_result(models.Model):
    type = models.CharField(primary_key=True, max_length=100)
    members = models.IntegerField(null=True, default=0)
    rounds = models.IntegerField(null=True, default=0)
    dev = models.BigIntegerField(null=True, default=0)
    num = models.BigIntegerField(null=True, default=0)

class score(models.Model):
    user = models.OneToOneField(userInfo, primary_key=True, on_delete=models.CASCADE)
    train_num = models.BigIntegerField(null=True, default=0)
    train_dev = models.BigIntegerField(null=True, default=0)
    train_rounds = models.IntegerField(null=True, default=0)
    exp_num = models.BigIntegerField(null=True, default=0)
    exp_dev = models.BigIntegerField(null=True, default=0)
    exp_rounds = models.IntegerField(null=True, default=0)
    latest_exp_time =  models.DateTimeField(null=True, default=timezone.now) 
    max_value = models.FloatField(null=True, default=0)

class group(models.Model):
    #创建组时确定的参数
    user = models.ForeignKey(userInfo, db_index=True, on_delete=models.CASCADE)
    ip = models.CharField(null=False, max_length=100)    
    rnd_num = models.SmallIntegerField(null=True, default=0)
    mod = models.BooleanField(default=False) 
    create_timestamp = models.DateTimeField(auto_now_add=True)

    #实验中更替的参数
    rounds = models.SmallIntegerField(null=True, default=0)  
    dev = models.IntegerField(null=True, default=0)  
    value = models.FloatField(null=True, default=0)
    max_value = models.FloatField(null=True, default=0)
    min_value = models.FloatField(null=True, default=0)
    last_edit_timestamp = models.DateTimeField(auto_now=True)
    curr_exp = models.BigIntegerField(null=True, default=0)
    compared = models.BooleanField(default=False, db_index=True) #用于标记是否已生成参照数

class experiment(models.Model):
    group = models.ForeignKey(group, db_index=True, on_delete=models.CASCADE)
    exp_score = models.SmallIntegerField(null=True, default=0)
    compare_score = models.SmallIntegerField(null=True, default=0)
    research_score = models.SmallIntegerField(null=True, default=0)
    create_timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.BooleanField(null=True, default=True) 




