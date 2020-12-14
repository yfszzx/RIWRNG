from django.core.management.base import BaseCommand
from main.models import *
from main.models import score as scr
import datetime
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
       print("Hello World")
       a = group.objects.all()
       for d in a:
            n = experiment.objects.filter(group_id=d.id).order_by('id').all()
            score = 0
            score_max = 0
            score_min = 0
            num = 1
            dev = 0
            for k in n:
                dev += (k.exp_score -5000) * (1 if k.direction else -1) 
                s = dev * 2 / ((10000 * num) ** 0.5)
                num += 1
                if s > score_max:
                   score_max = s
                if s < score_min:
                    score_min = s
            d.max_value = score_max
            d.min_value = score_min
            d.save()
            print(d)

       a = userInfo.objects.filter(grade__gt=0).all()
       for u in a:
            print(u)
            g = group.objects.filter(user_id=u.nid, mod=0).order_by('id').all()
            score = 0
            score_max = 0
            num = 1
            dev = 0
            for d in g:
                n = experiment.objects.filter(group_id=d.id).order_by('id').all()
                for k in n:
                    dev += (k.exp_score -5000) * (1 if k.direction else -1) 
                    s = dev * 2 / ((10000 * num) ** 0.5)
                    num += 1
                    if s > score_max:
                       score_max = s
            print(score_max)
            s = scr.objects.get(user_id=u.nid)
            s.max_value = score_max
            s.save()
            print(s)

             
