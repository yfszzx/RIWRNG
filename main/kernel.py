from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import rdrand as rd
from main.models import *
import time
RAND_NUMBER_NUM = 10000
def _get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip
def _get_rand_num():
    start = time.time()
    rnd = 0
    rnd_rsc = 0
    for i in range(RAND_NUMBER_NUM):
        num = rd.rdrand_get_bits(2) 
        m = num % 2
        rnd += m
        rnd_rsc += int((num - m) / 2)    
    return rnd, rnd_rsc, time.time() - start

#要求参数：groupid, mod
@login_required(login_url='/auth_error')   
def get_result(request): 
    groupid = int(request.GET["groupid"])
    mod = int(request.GET["mod"])
    if groupid == 0:
        usr = user.objects.get(user=request.user)
        grp = group.objects.create(
            user=usr,
            ip=_get_ip(request),
            rnd_num=RAND_NUMBER_NUM,
            mod=mod
            )     
        grp.save()   
    else:
        grp = group.objects.get(id=groupid)

    rnd, rnd_rsc, seconds = _get_rand_num()    
    exp = experiment.objects.create(
        group=grp,
        exp_score=rnd,
        research_score=rnd_rsc,
        )
    scr = score.objects.get(user=grp.user)
    if mod:
        scr.train_score = scr.train_score + rnd
        scr.train_num += RAND_NUMBER_NUM
    else:
        scr.exp_score += rnd
        scr.exp_num += RAND_NUMBER_NUM
   
    scr.save()
    grp.rounds += 1
    grp.curr_exp = exp.id
    grp.dev +=  rnd -  int(RAND_NUMBER_NUM / 2)
    grp.value = grp.dev * 2 / ((RAND_NUMBER_NUM * grp.rounds) ** 0.5)
    grp.compared = False
    grp.save()
    #测试模式授权
    if mod == 0 and grp.user.grade == 0 and grp.rounds >= 10 and grp.value > 3:
        grp.user.grade = 0
        grp.user.save()
    return JsonResponse({
        "groupid":grp.id, "rnd":rnd, "time":round(seconds * 1000, 2), 
        "dev":grp.dev,  "value": round(grp.value, 3)
     })

#要求参数：groupid
@login_required(login_url='/auth_error')   
def set_compare(request):
    def update_compare(grp):        
        rnd, _, _ =  _get_rand_num()
        experiment.objects.filter(id=grp.curr_exp).update(compare_score=rnd)
        grp.compared = True
        grp.save()
    groupid = int(request.GET["groupid"])
    grp = group.objects.get(id=groupid)
    update_compare(grp)
    if grp.rounds == 1:
        cmps = group.objects.filter(user=grp.user, compared=False)
        for grp in cmps:
            update_compare(grp)
    return JsonResponse({"round":grp.rounds})   



