from django.shortcuts import render
from django.http import HttpResponse
import requests as rq
import json
from django.shortcuts import redirect
from django.conf import settings
from main.models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

APPID = settings.WX_APPID
SECRET = settings.WX_SECRET

def _add_user(info):      
    #usr = ser.objects.create_user(username=info["openid"], password='password')
    obj = userInfo.objects.create_user(
        username=info["openid"], 
        password='password',
        sex=info["sex"],
        nickname=info["nickname"].encode('iso-8859-1').decode('utf-8'),
        headimgurl=info["headimgurl"]
    )
    obj.save()    
    score.objects.create(
        user=obj
    )
    return obj

def _auth_login(openid, request):
    usr = auth.authenticate(username=openid, password='password')
    if usr.is_active:
        auth.login(request, usr)   

@login_required(login_url='/auth_error')    
def exp_main(request):
    if request.GET["mod"] == 'e':
        usr = user.objects.get(user=request.user)
        if usr.grade == 0:
            return render(request, 'forbid.html')
    return render(request, 'experiment.html')


def auth_error(request):
    return render(request, 'login.html')

def login(request):
    code = request.GET['code']   
    req = rq.get(f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={SECRET}&code={code}&grant_type=authorization_code")
    req = json.loads(req.text)
    info = req
    if "errcode" in req.keys():
        return auth_error(request)
    if request.GET['state'] == 'userinfo':
        openid = req["openid"]
        token = req["access_token"]
        req = rq.get(f"https://api.weixin.qq.com/sns/userinfo?access_token={token}&openid={openid}&lang=zh_CN")
        info  =  json.loads(req.text)
        usr = _add_user(info)
    elif user.objects.filter(openid=req["openid"]).count() == 0:
            return redirect(f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri=http://psi.longmentcm.com/login&response_type=code&scope=snsapi_userinfo&state=userinfo#wechat_redirect")
    _auth_login(info["openid"], request)
    return redirect(f"/riwrng/main")

@login_required(login_url='/auth_error') 
def main(request):
    return render(request, 'main.html')


def test_login(request):   
    if not settings.LOCAL_DEBUD:
        return  render(request, 'login.html')
    openid = request.GET['openid']   
    usr_obj = userInfo.objects.filter(username=openid)
    if usr_obj.count() == 0:
        info = {"openid":openid, "sex":1, "nickname":"test_user", "headimgurl":"http://thirdwx.qlogo.cn/mmopen/vi_32/icmBarsam1EodnibzlPDoG1d7QcALr7EicYWfGlST4gIYBPqYjH8oxQuLnlRgLaSVRs5YyugWKO6ujJ3haUA3jq8Q/132" }
        usr = _add_user(info)
    usr = _auth_login(openid, request)
    return redirect(f"/riwrng/main")


def debug(request):
    if not settings.LOCAL_DEBUD:
        return  render(request, 'login.html')
    

@login_required(login_url='/auth_error') 
def performance(request):
    def scr(score, num):
        if num == 0:
            return 0
        return round(score * 2/ ((num  * 1000) ** 0.5), 2)
    def std(num):
        return round((num * 1000) ** 0.5 / 2 ,2)
    def total_data(context, head):
        data = total_result.objects.get(type=head)
        context[f"{head}_ttl_rnd"] = data.rounds
        context[f"{head}_ttl_mem"] = data.members
        context[f"{head}_ttl_dev"] = data.dev
        context[f"{head}_ttl_std"]  = std(data.num)
        context[f"{head}_ttl_score"] = scr(data.dev, data.num)
        return context

    scores = score.objects.get(user=request.user)
    context = {
        "trn_dev": scores.train_dev,
        "trn_std": std(scores.train_num),
        "trn_rounds": scores.train_rounds,
        "trn_score":  scr(scores.train_dev, scores.train_num),
        "exp_dev": scores.exp_dev,
        "exp_std": std(scores.exp_num),
        "exp_rounds": scores.exp_rounds,
        "exp_score": scr(scores.exp_dev, scores.exp_num),
        "total_content": [{"name":"总体", "field":"total"}] #, {"name":"练习","field":"train"},   {"name": "试验","field":"exp"}]
        }
   # for fld in context["total_content"]:

    for fld in ["", "_cmp", "_rsc"]:
        context = total_data(context, "train" + fld)
        context = total_data(context, "exp" + fld)
        context = total_data(context, "total" + fld)
    return render(request, "performance.html", context)

@login_required(login_url='/auth_error') 
def detail(request):
    grp = group.objects.filter(user=request.user, mod=request.GET["mod"]=='t')
    paginator = Paginator(grp, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page) 
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    for s in grp:
        s.value = round(s.value, 2)
    context ={"list":grp, "contacts":contacts}
    return render(request, 'detail.html', context)

def about(request):
    return render(request, 'about.html', {"title":"意念干扰随机数发生器实验"})
