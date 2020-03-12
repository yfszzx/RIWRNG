from django.shortcuts import render
from django.http import HttpResponse
import requests as rq
import json
from django.shortcuts import redirect

def main(request):
    code  = request.GET['code']
    return HttpResponse(code)
   #  if request.GET['state'] != 'userinfo':
   #       return redirect("https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx6742e22952f55f43&redirect_uri=http://psi.longmentcm.com/riwrng&response_type=code&scope=snsapi_userinfo&state=userinfo#wechat_redirect")
   #  r = rq.get(f"https://api.weixin.qq.com/sns/oauth2/access_token?appid=wx6742e22952f55f43&secret=7dc332250bc57fa4c8a46f980d112956&code={code}&grant_type=authorization_code")
   #  openid = json.loads(r.text)["openid"]
   #  if request.GET['state'] == 'userinfo':
   

   # https://api.weixin.qq.com/sns/userinfo?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN

