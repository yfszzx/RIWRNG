from django.http import HttpResponse
import json
#import rdrand as rd
import time
RAND_NUMBER_NUM = 10000
def _get_rand_num():
    start = time.time()
    rnd = 0
    rnd_rsc = 0
    for i in range(RAND_NUMBER_NUM):
        num = rd.rdrand_get_bits(2) 
        rnd += num % 2
        rnd_rsc += int((num - rnd) / 2)
    return rnd, rnd_rsc, time.time() - start

def _kernel(usr, mod, groupid):
    if groupid == 0:
        usr.group_num += 1
        usr.save()
        groupid = usr.group_num

    rnd, rnd_rsc, seconds = _get_rand_num()
    exp = experiment.objects.create(
        user=usr,
        rnd_num=RAND_NUMBER_NUM,
        exp_mod=mod,
        exp_score=rnd,
        research_score=rnd_rsc,
        group=groupid
        )
    scr = score.objects.get(user=usr)
    if mod == 't':
        scr.train_score += rnd
        scr.train_num += RAND_NUMBER_NUM
    elif mod == 'e':
        scr.exp_score += rnd
        scr.exp_num += RAND_NUMBER_NUM
    elif mod == 'v':
        scr.verify_score += rnd
        scr.verify_num += RAND_NUMBER_NUM
    scr.save()
    return rnd, groupid, exp.id, seconds

#要求参数：groupid, mod
@login_required(login_url='/auth_error')   
def get_result(request):
    num, groupid, expid, seconds = _kernel(request.user, request.GET["mod"], request.GET["groupid"])    
    return  JsonResponse({"rnd":num, "time":seconds, "num":RAND_NUMBER_NUM, "expid":expid, "groupid":groupid})
#要求参数：expid
@login_required(login_url='/auth_error')   
def set_compare(request):
    rnd, _, _ =  _get_rand_num()
    experiment.objects.filter(id=request.GET["expid"]).update(compare_score=rnd)
    return JsonResponse(["OK"])

