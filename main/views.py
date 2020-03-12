from django.shortcuts import render
from django.http import HttpResponse
import requests as rq
import json
from django.shortcuts import redirect
from django.conf import settings
from main.models import *
APPID = settings.WX_APPID
SECRET = settings.WX_SECRET

def _add_user(req):
    jsn =  json.loads(req.text)
    openid = jsn["openid"]
    token = jsn["access_token"]
    req = rq.get(f"https://api.weixin.qq.com/sns/userinfo?access_token={token}&openid={openid}&lang=zh_CN")

    info  =  json.loads(req.text)
    obj = user(
        openid=openid,
        sex=info["sex"],
        nickname=info["nickname"],
        headimgurl=info["headimgurl"]
    )
    obj.save()
    return obj

def main(request):
    code = request.GET['code']   
    req = rq.get(f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={SECRET}&code={code}&grant_type=authorization_code")
    if request.GET['state'] == 'userinfo':
        usr = _add_user(req)
    else:
        openid = json.loads(req.text)["openid"]
        usr_obj = user.objects.filter(openid=openid)
        if usr_obj.count() == 0:
            return redirect(f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri=http://psi.longmentcm.com/riwrng&response_type=code&scope=snsapi_userinfo&state=userinfo#wechat_redirect")
        else:
            usr = usr_obj.get(openid=openid)
    return HttpResponse(usr.nickname)

def test(request):   
    openid = request.GET['openid']   
    usr_obj = user.objects.filter(openid=openid)
    if usr_obj.count() == 0:
        usr = user(
            openid=openid,
            sex=request.GET['sex'],
            nickname=request.GET['nickname'],
            headimgurl=request.GET['headimgurl']
        )
        usr.save()
    else:
        usr = usr_obj.get(openid=openid)
    return render(request, 'riwrng.html')


