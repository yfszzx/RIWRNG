from django.core.management.base import BaseCommand
from main.models import *
from main.models import score as scr
import datetime
from django.db.models import Avg
import time
import numpy as np
class Command(BaseCommand):
    def handle(self, *args, **options):
        s1 = np.array(experiment.objects.filter(compare_score__gt=0).values_list("compare_score",flat=True))
        s2 = np.array(experiment.objects.filter(compare_score__gt=0).values_list("direction",flat=True))
        s2 = s2 * 2 - 1
        print(((s1-5000)*s2).mean())

        
            
        
      