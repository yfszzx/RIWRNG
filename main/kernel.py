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

def _get_dev(rnd, direct):
        return (rnd - RAND_NUMBER_NUM / 2) * (1 if direct else -1) 

def _total_save(head, member, rnd, direct):
        tr = total_result.objects.get(type=head)
        tr.rounds += 1
        tr.dev += _get_dev(rnd, direct)
        tr.num += RAND_NUMBER_NUM /1000
        tr.members += member
        tr.save() 

#要求参数：groupid, mod, direction
@login_required(login_url='/auth_error')   
def get_result(request): 
    groupid = int(request.GET["groupid"])
    mod = int(request.GET["mod"])
    direct = int(request.GET["direction"])

    if groupid == 0:
        grp = group.objects.create(
            user=request.user,
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
        direction=direct
        )

    scr = score.objects.get(user=grp.user)
    if mod:
        tp = "train"
        member = 1 if scr.train_rounds == 0 else 0
        scr.train_dev  += _get_dev(rnd, direct)
        scr.train_num += RAND_NUMBER_NUM / 1000
        scr.train_rounds += 1
    else:
        member = 1 if scr.exp_rounds == 0 else 0
        scr.exp_dev += _get_dev(rnd, direct)
        scr.exp_num += RAND_NUMBER_NUM / 1000
        scr.exp_rounds += 1
        val = scr.exp_dev * 2 / (scr.exp_num * 1000) ** 0.5
        if val > scr.max_value:
            scr.max_value = val
            scr.max_rounds = scr.exp_rounds
        tp = "exp"
    scr.save()
    _total_save(tp, member, rnd, direct)
    _total_save("total", 1 if member == 1 and tp == "train" else 0, rnd, direct)
    _total_save(tp + "_rsc", 0, rnd_rsc, direct)
    _total_save("total" + "_rsc", 0, rnd_rsc, direct)
    
    
    grp.rounds += 1
    grp.curr_exp = exp.id
    grp.dev +=  _get_dev(rnd, direct)
    grp.value = grp.dev * 2 / ((RAND_NUMBER_NUM * grp.rounds) ** 0.5)
    grp.compared = False
    if grp.max_value < grp.value:
        grp.max_value = grp.value
        grp.max_rounds = grp.rounds
    if grp.min_value > grp.value:
        grp.min_value = grp.value
    grp.save()
    
    if direct != grp.user.direction:
        grp.user.direction = direct
        grp.user.save()

    #测试模式授权
    if mod == 1 and grp.user.grade == 0 and grp.rounds >= 20 and grp.value >= 3:
        grp.user.grade = 1
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
        exp = experiment.objects.get(id=grp.curr_exp)
        exp.compare_score = rnd
        exp.save()
        grp.compared = True
        grp.save()
        tp = "train" if grp.mod else "exp"
        _total_save(tp + "_cmp", 0, rnd, exp.direction)
        _total_save("total_cmp", 0, rnd, exp.direction)    

    groupid = int(request.GET["groupid"])
    grp = group.objects.get(id=groupid)
    update_compare(grp)
    if grp.rounds == 1:
        cmps = group.objects.filter(user=grp.user, compared=False)
        for grp in cmps:
            update_compare(grp)
    return JsonResponse({"round":grp.rounds})   



