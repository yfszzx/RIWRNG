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
    return  user.objects.get(user=usr)

#@login_required(login_url='/auth_error')    
def exp_main(request):
    return render(request, 'experiment.html')


def auth_error(request):
    return render(request, 'login.html')

def login(request):
    code = request.GET['code']   
    req = rq.get(f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={SECRET}&code={code}&grant_type=authorization_code")
    req = json.loads(req.text)
    if "errcode" in req.keys():
        return auth_error(request)
    if request.GET['state'] == 'userinfo':
        openid = req["openid"]
        token = req["access_token"]
        req = rq.get(f"https://api.weixin.qq.com/sns/userinfo?access_token={token}&openid={openid}&lang=zh_CN")
        info  =  json.loads(req.text)
        usr = _add_user(info)
    elif user.objects.filter(openid=req["openid"]).count() == 0:
            return redirect(f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri=http://psi.longmentcm.com/riwrng&response_type=code&scope=snsapi_userinfo&state=userinfo#wechat_redirect")
    usr = _auth_login(req["openid"], request)
    context = {'usr':usr}
    return render(request, 'main.html', context)


def test_login(request):   
    openid = request.GET['openid']   
    usr_obj = user.objects.filter(openid=openid)
    if usr_obj.count() == 0:
        info = {"openid":openid, "sex":1, "nickname":"test_user", "headimgurl":"http://thirdwx.qlogo.cn/mmopen/vi_32/icmBarsam1EodnibzlPDoG1d7QcALr7EicYWfGlST4gIYBPqYjH8oxQuLnlRgLaSVRs5YyugWKO6ujJ3haUA3jq8Q/132" }
        usr = _add_user(info)
    usr = _auth_login(openid, request)
    context = {'usr':usr}
    return render(request, 'main.html', context)


def debug(request):
    ret = rq.get("http://psi.longmentcm.com/riwrng/getNum")
    return JsonResponse(json.loads(ret.text))


