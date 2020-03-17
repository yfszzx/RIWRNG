from django.shortcuts import render
from django.http import HttpResponse
import requests as rq
import json
from django.shortcuts import redirect
from django.conf import settings
from main.models import *
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

APPID = settings.WX_APPID
SECRET = settings.WX_SECRET

def _add_user(info):      
    usr = User.objects.create_user(username=info["openid"], password='password')
    obj = user(
        user=usr,
        openid=info["openid"],
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
    return render(request, 'main.html', {"usr": user.objects.get(user=request.user)})


def test_login(request):   
    openid = request.GET['openid']   
    usr_obj = user.objects.filter(openid=openid)
    if usr_obj.count() == 0:
        info = {"openid":openid, "sex":1, "nickname":"test_user", "headimgurl":"http://thirdwx.qlogo.cn/mmopen/vi_32/icmBarsam1EodnibzlPDoG1d7QcALr7EicYWfGlST4gIYBPqYjH8oxQuLnlRgLaSVRs5YyugWKO6ujJ3haUA3jq8Q/132" }
        usr = _add_user(info)
    usr = _auth_login(openid, request)
    return redirect(f"/riwrng/main")


def debug(request):
    ret = rq.get("http://psi.longmentcm.com/riwrng/getNum")
    return JsonResponse(json.loads(ret.text))

@login_required(login_url='/auth_error') 
def performance(request):
    def scr(score, num):
        if num == 0:
            return 0
        return round((score - num/2) * 2/ (num ** 0.5), 2)
    def std(num):
        return round(num ** 0.5 / 2 ,2)
    usr = user.objects.get(user=request.user)
    scores = score.objects.get(user=usr)
    context = {
        "trn_dev": scores.train_score - scores.train_num/2,
        "trn_std": std(scores.train_num),
        "trn_rounds": scores.train_rounds,
        "trn_score":  scr(scores.train_score, scores.train_num),
        "exp_dev": scores.exp_score - scores.exp_num/2,
        "exp_std": std(scores.exp_num),
        "exp_rounds": scores.exp_rounds,
        "exp_score": scr(scores.exp_score, scores.exp_num)
        }
    return render(request, "performance.html", context)

@login_required(login_url='/auth_error') 
def detail(request):
    usr = user.objects.get(user=request.user)
    grp = group.objects.filter(user=usr, mod=request.GET["mod"]=='t')
    paginator = Paginator(grp, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page) # contactsΪPage����
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    for s in grp:
        s.value = round(s.value, 2)
    context ={"list":grp, "contacts":contacts}
    return render(request, 'detail.html', context)
